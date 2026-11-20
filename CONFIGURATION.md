# Configuration
Priority: committed `config.json` defaults, ignored `config.local.json`, then process environment / private `.env` overrides.

SORA and SHADOW default to the local llama.cpp server at `http://127.0.0.1:8080/v1`; the app starts and supervises `llama-server` with the configured GGUF. Both use separate prompts and mode settings, while the local server loads the mode-specific model path. JARVIS uses its own stable-diffusion.cpp process. The process manager terminates the prior managed engine before another starts.

Remote chat: set `CUSTOM_BASE_URL`, `CUSTOM_API_KEY`, `CUSTOM_MODEL`; then choose remote backend for SORA/SHADOW. Remote image: set `IMAGE_BASE_URL`, `IMAGE_API_KEY`, `IMAGE_MODEL`; it must implement OpenAI-compatible `POST /images/generations` and return `b64_json` or `url`. These are independent providers.

Never commit `.env` or `config.local.json`. Example files contain placeholders only. Run `python config_loader.py` to validate configuration.
