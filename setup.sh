#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
pkg update -y
pkg install -y python git
mkdir -p models outputs "$HOME/ai-workspace"
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
if [ ! -f .env ]; then cp .env.example .env; fi
if [ ! -f config.local.json ]; then cp config.local.example.json config.local.json; fi
python config_loader.py
python -m unittest discover -s tests -v
printf '\nSetup complete. Configure private .env/config.local.json and install compatible llama.cpp / stable-diffusion.cpp binaries.\n'
