# Vivo / Termux installation
1. Install Termux and Termux:API from the same maintained source. Do not mix signing sources.
2. In Termux: `pkg update && pkg upgrade -y && pkg install -y python git clang cmake make`.
3. Clone the repository, create a venv, and run the test suite as shown in README.
4. Put a compatible GGUF file at `models/llm.gguf`; edit `config.local.json` to point SORA/SHADOW at it.
5. Build/install a Termux-compatible llama.cpp `llama-server` binary and ensure it is on PATH.
6. For local JARVIS, build/install stable-diffusion.cpp `sd` and configure the actual model file path. Local diffusion performance on mobile is not guaranteed; remote image mode is a supported alternative.
7. Copy `.env.example` to `.env`; edit credentials locally only. Never paste secrets into chat or commit them.
8. Run `python config_loader.py`, `python -m unittest discover -s tests -v`, then `python main.py`.

Android 12 permission prompts and Termux:API companion permissions must be granted on the phone. The CLI cannot remotely verify microphone access, thermal behavior, or actual model inference performance.
