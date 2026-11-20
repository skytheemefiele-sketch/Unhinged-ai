"""Load and validate configuration, including private .env overrides."""
from __future__ import annotations
import copy
import json
import os
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent

def _load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value

def _merge(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(base)
    for key, value in overlay.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result

def _read_json(path: Path, required: bool = False) -> dict[str, Any]:
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
    root = Path(root) if root is not None else ROOT
    _load_dotenv(root / ".env")
    cfg = _merge(_read_json(root / "config.json", True), _read_json(root / "config.local.json"))
    remote = cfg.setdefault("remote", {})
    image = cfg.setdefault("remote_image", {})
    for key, env in (("base_url", "CUSTOM_BASE_URL"), ("api_key", "CUSTOM_API_KEY"), ("model", "CUSTOM_MODEL")):
        if os.getenv(env):
            remote[key] = os.environ[env]
    if any(remote.get(k) for k in ("base_url", "api_key", "model")):
        remote["enabled"] = True
    for key, env in (("base_url", "IMAGE_BASE_URL"), ("api_key", "IMAGE_API_KEY"), ("model", "IMAGE_MODEL")):
        if os.getenv(env):
            image[key] = os.environ[env]
    if any(image.get(k) for k in ("base_url", "api_key", "model")):
        image["enabled"] = True
    for mode in ("sora", "shadow", "jarvis"):
        override = os.getenv(f"UNHINGED_{mode.upper()}_BACKEND")
        if override:
            if override not in ("local", "remote"):
                raise ValueError(f"UNHINGED_{mode.upper()}_BACKEND must be local or remote")
            cfg["modes"][mode]["backend"] = override
    validate_config(cfg)
    return cfg

def validate_config(cfg: dict[str, Any]) -> None:
    modes = cfg.get("modes", {})
    missing = {"sora", "shadow", "jarvis"} - set(modes)
    if missing:
        raise ValueError(f"Missing mode configuration(s): {', '.join(sorted(missing))}")
    if cfg.get("runtime", {}).get("max_heavy_engines_active") != 1:
        raise ValueError("max_heavy_engines_active must equal 1")
    for mode in ("sora", "shadow"):
        backend = modes[mode].get("backend")
        if backend not in ("local", "remote"):
            raise ValueError(f"modes.{mode}.backend must be local or remote")
        if backend == "remote" and not cfg.get("remote", {}).get("enabled"):
            raise ValueError(f"{mode} selects remote but remote is disabled")
    for section in ("remote", "remote_image"):
        item = cfg.get(section, {})
        if item.get("enabled"):
            for key in ("base_url", "api_key", "model"):
                if not item.get(key):
                    raise ValueError(f"{section} is enabled but {section}.{key} is empty")
            if not item["base_url"].startswith(("http://", "https://")):
                raise ValueError(f"{section}.base_url must be HTTP(S)")
    if modes["jarvis"].get("engine") != "stable_diffusion_cpp":
        raise ValueError("JARVIS must use stable_diffusion_cpp")
    if modes["jarvis"].get("backend", "local") not in ("local", "remote"):
        raise ValueError("modes.jarvis.backend must be local or remote")
    if modes["jarvis"].get("backend") == "remote" and not cfg.get("remote_image", {}).get("enabled"):
        raise ValueError("JARVIS selects remote but remote_image is disabled")

if __name__ == "__main__":
    cfg = load_config()
    print(json.dumps({
        "mode_names": list(cfg["modes"]),
        "active_engine_limit": cfg["runtime"]["max_heavy_engines_active"],
        "remote_enabled": cfg["remote"]["enabled"],
        "remote_image_enabled": cfg["remote_image"]["enabled"]
    }, indent=2))
