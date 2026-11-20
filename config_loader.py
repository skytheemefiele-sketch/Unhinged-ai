"""Load and validate Unhinged AI configuration without third-party dependencies."""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "config.json"
LOCAL_PATH = ROOT / "config.local.json"


def _merge(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(base)
    for key, value in overlay.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def _read_json(path: Path, *, required: bool = False) -> dict[str, Any]:
    if not path.exists():
        if required:
            raise FileNotFoundError(f"Required configuration file not found: {path}")
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"Top-level JSON value in {path} must be an object")
    return data


def load_config(root: Path | str | None = None) -> dict[str, Any]:
    """Load defaults, then private config.local.json, then environment overrides."""
    root = Path(root) if root is not None else ROOT
    config = _merge(_read_json(root / "config.json", required=True),
                    _read_json(root / "config.local.json"))

    remote = config.setdefault("remote", {})
    env_values = {
        "base_url": os.getenv("CUSTOM_BASE_URL"),
        "api_key": os.getenv("CUSTOM_API_KEY"),
        "model": os.getenv("CUSTOM_MODEL"),
    }
    for key, value in env_values.items():
        if value:
            remote[key] = value
    if any(env_values.values()):
        remote["enabled"] = True

    for mode in ("sora", "shadow"):
        override = os.getenv(f"UNHINGED_{mode.upper()}_BACKEND")
        if override:
            if override not in ("local", "remote"):
                raise ValueError(f"UNHINGED_{mode.upper()}_BACKEND must be local or remote")
            config["modes"][mode]["backend"] = override

    validate_config(config)
    return config


def validate_config(config: dict[str, Any]) -> None:
    modes = config.get("modes", {})
    missing = {"sora", "shadow", "jarvis"} - set(modes)
    if missing:
        raise ValueError(f"Missing mode configuration(s): {', '.join(sorted(missing))}")
    if config.get("runtime", {}).get("max_heavy_engines_active") != 1:
        raise ValueError("This device profile requires max_heavy_engines_active = 1")
    remote = config.get("remote", {})
    if remote.get("enabled"):
        for key in ("base_url", "api_key", "model"):
            if not remote.get(key):
                raise ValueError(f"Remote endpoint is enabled but remote.{key} is empty")
        if not str(remote["base_url"]).startswith(("http://", "https://")):
            raise ValueError("remote.base_url must start with http:// or https://")
    for mode in ("sora", "shadow"):
        backend = modes[mode].get("backend")
        if backend not in ("local", "remote"):
            raise ValueError(f"modes.{mode}.backend must be local or remote")
        if backend == "remote" and not remote.get("enabled"):
            raise ValueError(f"modes.{mode} selects remote but the remote endpoint is disabled")
    if modes["jarvis"].get("engine") != "stable_diffusion_cpp":
        raise ValueError("JARVIS must use its separate stable_diffusion_cpp engine")


if __name__ == "__main__":
    cfg = load_config()
    print(json.dumps({
        "default_mode": cfg["runtime"]["default_mode"],
        "active_engine_limit": cfg["runtime"]["max_heavy_engines_active"],
        "sora_backend": cfg["modes"]["sora"]["backend"],
        "shadow_backend": cfg["modes"]["shadow"]["backend"],
        "jarvis_backend": cfg["modes"]["jarvis"]["backend"],
        "remote_enabled": cfg["remote"]["enabled"],
        "remote_api_key_configured": bool(cfg["remote"].get("api_key")),
    }, indent=2))
