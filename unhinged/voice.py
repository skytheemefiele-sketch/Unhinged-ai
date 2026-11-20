"""Termux:API voice helpers with graceful non-Termux fallback."""
import shutil, subprocess

def speak(text: str):
    exe=shutil.which("termux-tts-speak")
    if not exe: raise RuntimeError("termux-tts-speak unavailable; install Termux:API")
    subprocess.run([exe, text], check=True, timeout=90)

def listen():
    exe=shutil.which("termux-speech-to-text")
    if not exe: raise RuntimeError("termux-speech-to-text unavailable; install Termux:API")
    result=subprocess.run([exe],capture_output=True,text=True,check=True,timeout=120)
    return result.stdout.strip()
