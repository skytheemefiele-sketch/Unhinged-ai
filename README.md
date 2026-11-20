# Unhinged AI

A local-first, three-mode personal assistant designed for Android/Termux.

## Modes
- **SORA** — personal assistant using a local llama.cpp OpenAI-compatible endpoint by default; optional remote OpenAI-compatible endpoint.
- **SHADOW** — workspace-scoped coding/file assistant. Shell commands require explicit confirmation.
- **JARVIS** — isolated stable-diffusion.cpp image generation process.

Only one heavy local engine may run at a time. The process supervisor terminates the prior process group before starting another. This is intended to reduce memory pressure and heat on the Vivo Y-series Android 12 device; actual performance depends on the exact SoC, RAM, model, and backend build.

## Install on Termux
Install Termux and Termux:API from the same trusted distribution source, then:

```sh
pkg update && pkg upgrade -y
pkg install -y python git
git clone https://github.com/skytheemefiele-sketch/Unhinged-ai.git
cd Unhinged-ai
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python main.py
```

Edit `config.local.json` for local model names and paths. Install/build llama.cpp and stable-diffusion.cpp separately for a compatible Android ARM64 environment. Start the llama.cpp server at `127.0.0.1:8080` when using local SORA/SHADOW.

## Commands
`/sora`, `/shadow`, `/jarvis`, `/voice`, `/status`, `/exit`.

## Private remote endpoint
Set `CUSTOM_BASE_URL`, `CUSTOM_API_KEY`, and `CUSTOM_MODEL` in `.env` or `config.local.json`. Select remote routing for SORA or SHADOW using the mode backend setting or `UNHINGED_SORA_BACKEND=remote`. Never commit `.env` or `config.local.json`.

## Gmail and voice
Gmail needs `AI_GMAIL_USER` and `AI_GMAIL_APP_PASS` configured privately. Sending email requires explicit confirmation in the interactive application before use. Voice requires Termux:API. These integrations are optional.

## Tests
```sh
python -m unittest discover -s tests -v
python config_loader.py
```

## Safety and limitations
- File operations are restricted to `~/ai-workspace`.
- Shell tool execution is denied unless the caller explicitly confirms it; model tool calls cannot silently authorize shell commands.
- Web fetch only allows HTTPS and blocks obvious local host targets. Use caution with untrusted URLs.
- The generic remote endpoint is a chat endpoint; it does not imply remote image generation.
- Local image generation on mobile may be slow, unsupported, or thermally constrained. JARVIS can use a future remote image adapter; that adapter is not yet included in this release.
- Never put API keys, Gmail app passwords, personal mail, model weights, or generated images in this public repository.
