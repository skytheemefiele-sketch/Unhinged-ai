"""Single-heavy-engine supervisor for Android/Termux."""
from __future__ import annotations
import os, signal, subprocess, threading, time
from dataclasses import dataclass
from typing import Optional

@dataclass
class EngineProcess:
    name: str
    process: subprocess.Popen
    command: list[str]

class EngineManager:
    """Ensures at most one local heavy process is running at a time."""
    def __init__(self, config: dict):
        self.config = config
        self._active: Optional[EngineProcess] = None
        self._lock = threading.RLock()

    @property
    def active_name(self):
        return self._active.name if self._active and self._active.process.poll() is None else None

    def stop(self, timeout: float | None = None):
        with self._lock:
            item = self._active
            if not item:
                return
            proc = item.process
            if proc.poll() is None:
                try:
                    if os.name == "posix":
                        os.killpg(proc.pid, signal.SIGTERM)
                    else:
                        proc.terminate()
                    proc.wait(timeout=timeout or self.config["runtime"].get("shutdown_timeout_seconds", 20))
                except subprocess.TimeoutExpired:
                    if os.name == "posix":
                        os.killpg(proc.pid, signal.SIGKILL)
                    else:
                        proc.kill()
                    proc.wait()
            self._active = None

    def start(self, name: str, command: list[str], cwd=None, env=None):
        if name not in ("sora", "shadow", "jarvis"):
            raise ValueError("Unknown engine mode")
        with self._lock:
            self.stop()
            if not command:
                raise ValueError("Engine command cannot be empty")
            kwargs = {"cwd": cwd, "env": env, "stdin": subprocess.DEVNULL}
            if os.name == "posix":
                kwargs["start_new_session"] = True
            proc = subprocess.Popen(command, **kwargs)
            self._active = EngineProcess(name, proc, command)
            return proc

    def close(self):
        self.stop()
