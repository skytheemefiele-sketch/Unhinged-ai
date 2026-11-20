# Configuration
Priority: committed `config.json` defaults, ignored `config.local.json`, then process environment / private `.env` overrides.

SORA and SHADOW default to the local llama.cpp OpenAI-compatible server at `http://127.0.0.1:8080/v1`; the app starts and supervises `llama-server` with the configured GGUF. Both use separate prompts and mode settings. JARVIS defaults to its separate stable-diffusion.cpp process. The supervisor terminates the previous managed engine before starting another.

Remote chat: set `CUSTOM_BASE_URL`, `CUSTOM_API_KEY`, and `CUSTOM_MODEL`; then select remote for SORA and/or SHADOW using `UNHINGED_SORA_BACKEND=remote`, `UNHINGED_SHADOW_BACKEND=remote`, or the matching `modes.*.backend` values.

Remote image: set `IMAGE_BASE_URL`, `IMAGE_API_KEY`, and `IMAGE_MODEL`; the endpoint must implement OpenAI-compatible `POST /images/generations` and return `b64_json` or `url`. Then select remote JARVIS with `UNHINGED_JARVIS_BACKEND=remote` or `modes.jarvis.backend=remote`. JARVIS remains local by default even when image endpoint credentials are present.

Never commit `.env` or `config.local.json`. Example files contain placeholders only. Run `python config_loader.py` to validate configuration.
