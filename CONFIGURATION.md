# Configuration

Unhinged AI loads configuration in this order (later values win):

1. `config.json` — safe, committed defaults; local-only operation is the default.
2. `config.local.json` — optional private machine configuration; ignored by Git.
3. Environment variables — highest-priority overrides for private remote credentials.

## Local-first defaults

- SORA and SHADOW use the local llama.cpp OpenAI-compatible server at `http://127.0.0.1:8080/v1`.
- JARVIS uses a separate `stable-diffusion.cpp` `sd` executable and its own model/output paths.
- The runtime is configured to allow only one heavy engine at a time. The mode supervisor must stop and confirm shutdown of the previous engine before starting another; configuration alone does not enforce process isolation.

## Optional OpenAI-compatible endpoint

Copy `config.local.example.json` to `config.local.json`, then set the endpoint details there, or create a private `.env` from `.env.example`:

```sh
cp .env.example .env
```

Set `CUSTOM_BASE_URL`, `CUSTOM_API_KEY`, and `CUSTOM_MODEL`. When these environment variables are present, the remote endpoint is enabled. To route SORA or SHADOW remotely, set that mode's `backend` to `remote` in `config.local.json`, or set `UNHINGED_SORA_BACKEND=remote` / `UNHINGED_SHADOW_BACKEND=remote`. Both modes remain local by default.

The custom endpoint is for OpenAI-compatible chat/completions. It does not automatically provide image generation: JARVIS remains on its isolated local image engine unless a separate image-provider integration is implemented and configured.

## Security

Never commit `config.local.json`, `.env`, API keys, Gmail app passwords, model weights, or generated outputs. The repository is public. Use placeholders in examples only. Do not paste credentials into chat or source files.

## Validate

Run:

```sh
python config_loader.py
```

The loader validates the three distinct modes, enforces the single-heavy-engine configuration, and checks that remote settings are complete before a remote backend is selected.
