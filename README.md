# Unhinged AI

Local-first, three-mode personal assistant for Android/Termux.

- **SORA:** personal assistant; local llama.cpp by default, optional OpenAI-compatible chat endpoint.
- **SHADOW:** workspace-scoped developer assistant; file tools and shell execution with per-command confirmation.
- **JARVIS:** separate stable-diffusion.cpp local image process or an independently configured OpenAI-compatible image endpoint.

The process manager stops its previously managed local heavy process before starting another. This is intended to reduce memory pressure and heat on the Vivo Y-series Android 12 device. It cannot guarantee performance; confirm the exact chipset/RAM and benchmark models on-device.

## Termux install
Install Termux and the Termux:API Android companion from the same maintained distribution source. Then:

```sh
pkg update && pkg upgrade -y
pkg install -y python git clang cmake make termux-api
git clone https://github.com/skytheemefiele-sketch/Unhinged-ai.git
cd Unhinged-ai
bash setup.sh
```

Put a compatible GGUF at `models/llm.gguf`; install a Termux-compatible `llama-server` binary on PATH. The app launches and supervises it locally on `127.0.0.1:8080`. Configure `modes.sora.model_path` and `modes.shadow.model_path` in private `config.local.json` if needed.

For local JARVIS, install a compatible stable-diffusion.cpp `sd` binary and set `modes.jarvis.model_path` to its model. On-device diffusion may be very slow or unsupported on this mobile chipset. Remote image generation is separately configured and does not share the LLM API credentials.

## Commands
`/sora`, `/shadow`, `/jarvis`, `/voice`, `/status`, `/exit`.

## Private configuration
Copy `.env.example` to `.env`. Set `CUSTOM_BASE_URL`, `CUSTOM_API_KEY`, and `CUSTOM_MODEL` for remote chat; route SORA or SHADOW by setting `UNHINGED_SORA_BACKEND=remote` or `UNHINGED_SHADOW_BACKEND=remote`. For remote image generation set `IMAGE_BASE_URL`, `IMAGE_API_KEY`, and `IMAGE_MODEL` to an OpenAI-compatible `/images/generations` provider, then set `UNHINGED_JARVIS_BACKEND=remote` (or `modes.jarvis.backend=remote` in `config.local.json`). JARVIS stays local by default. Or set these under `remote` / `remote_image` in ignored `config.local.json`.

Gmail optionally uses `AI_GMAIL_USER` and `AI_GMAIL_APP_PASS`. Sending mail prompts for confirmation. Voice requires Termux:API. Never commit `.env`, `config.local.json`, secrets, model weights, inbox contents, or generated images.

## Render QA
Render's test build command is `python -m unittest discover -s tests -v && python config_loader.py`; the optional health endpoint is `python qa_server.py`. Render does not host the Android local models, Gmail credentials, or Termux hardware APIs. No GitHub Actions workflow is required.

## Tests
```sh
python -m unittest discover -s tests -v
python config_loader.py
```

## Security and known limitations
- File tools are confined to `~/ai-workspace`.
- Shell execution requires interactive approval and runs without `shell=True`; still review commands before approval.
- Web fetching is HTTPS-only and blocks obvious localhost names, but DNS-rebinding/private-IP defenses should be strengthened before treating arbitrary URLs as fully safe.
- Gmail uses app-password IMAP/SMTP; OAuth is not implemented.
- Remote image support expects an OpenAI-compatible `POST /images/generations` endpoint returning base64 or URL data.
- Android microphone, TTS, local inference, GPU support, thermal behavior, and model performance require real-device acceptance testing.
