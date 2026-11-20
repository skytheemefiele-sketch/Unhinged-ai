"""CLI orchestration for SORA, SHADOW, and JARVIS."""
from __future__ import annotations
import os, json, shlex, shutil
from pathlib import Path
from .llm import chat
from .engines import EngineManager
from .tools import ToolBox, ToolError
from .parser import extract_tool_calls
from .voice import speak, listen

ROOT=Path(__file__).resolve().parent.parent

PROMPTS={
"sora":"You are SORA, a practical personal assistant. Use tools only when needed. Never claim an action succeeded unless the tool confirms it.",
"shadow":"You are SHADOW, a careful coding assistant. Work only inside the configured workspace. Ask for explicit confirmation before shell commands or destructive changes.",
"jarvis":"You are JARVIS, an image-generation assistant. Generate images only through the configured stable-diffusion.cpp executable; explain when it is unavailable."
}

class App:
    def __init__(self):
        from config_loader import load_config
        self.cfg=load_config(ROOT)
        self.mode=self.cfg["runtime"].get("default_mode","sora")
        self.engines=EngineManager(self.cfg)
        self.tools=ToolBox(os.getenv("AI_WORKSPACE",str(Path.home()/"ai-workspace")),self.cfg)
        self.history=[]

    def switch(self, mode):
        if mode not in PROMPTS: raise ValueError("Mode must be sora, shadow, or jarvis")
        self.engines.stop()
        self.mode=mode; self.history=[]
        print(f"Switched to {mode.upper()}; previous local engine stopped.")

    def _backend(self):
        mode=self.cfg["modes"][self.mode]
        if self.mode=="jarvis": return None
        if mode["backend"]=="remote":
            remote=self.cfg["remote"]
            return remote["base_url"],remote["model"],remote["api_key"]
        local=self.cfg["local"]["llm"]
        model=mode.get("model") or "local"
        return local["base_url"],model,local.get("api_key","")

    def _dispatch(self, call):
        name=call.get("tool"); args=call.get("arguments",{})
        if not isinstance(args,dict): raise ToolError("Tool arguments must be an object")
        if name=="file_read": return self.tools.file_read(args["path"])
        if name=="file_write": return self.tools.file_write(args["path"],args["content"])
        if name=="file_patch": return self.tools.file_patch(args["path"],args["old"],args["new"])
        if name=="file_list": return self.tools.file_list(args.get("path","."))
        if name=="shell_exec": return self.tools.shell_exec(args["command"],confirm=False)
        if name=="web_search": return self.tools.web_search(args["query"])
        if name=="web_fetch": return self.tools.web_fetch(args["url"])
        if name=="voice_say": return speak(args["text"])
        if name=="voice_listen": return listen()
        if name=="image_generate": return self._image(args["prompt"])
        if name=="gmail_check_codes":
            from .gmail_tools import GmailClient
            return GmailClient().recent_messages()
        if name=="gmail_send":
            raise ToolError("Email sending is only available through the interactive confirmation flow; use the dedicated CLI prompt.")
        raise ToolError(f"Unknown tool: {name}")

    def _image(self,prompt):
        cfg=self.cfg["modes"]["jarvis"]
        exe=shutil.which(cfg.get("executable","sd"))
        if not exe: raise ToolError("stable-diffusion.cpp 'sd' executable is not installed")
        out=Path(cfg.get("output_dir","outputs")); out.mkdir(exist_ok=True)
        target=out/"jarvis-output.png"
        self.engines.start("jarvis",[exe,"-p",prompt,"-o",str(target)])
        proc=self.engines._active.process; code=proc.wait(); self.engines._active=None
        if code: raise ToolError(f"Image engine exited with status {code}")
        return f"Image saved to {target}"

    def ask(self, text):
        if self.mode=="jarvis":
            print(self._image(text)); return
        base,model,key=self._backend()
        if not self.history: self.history=[{"role":"system","content":PROMPTS[self.mode]}]
        self.history.append({"role":"user","content":text})
        answer=chat(base,model,self.history,key)
        calls=extract_tool_calls(answer)
        if calls:
            for call in calls:
                try: result=self._dispatch(call)
                except Exception as exc: result={"error":str(exc)}
                self.history.append({"role":"tool","content":json.dumps(result,default=str)})
            answer=chat(base,model,self.history,key)
        self.history.append({"role":"assistant","content":answer})
        print(answer)

    def run(self):
        print("Unhinged AI — /sora /shadow /jarvis /voice /status /exit")
        try:
            while True:
                try: line=input(f"{self.mode.upper()}> ").strip()
                except (EOFError,KeyboardInterrupt): break
                if not line: continue
                if line=="/exit": break
                if line in ("/sora","/shadow","/jarvis"): self.switch(line[1:]); continue
                if line=="/status":
                    print(json.dumps({"mode":self.mode,"active_local_engine":self.engines.active_name,"workspace":str(self.tools.workspace)},indent=2)); continue
                if line=="/voice":
                    try: line=listen()
                    except Exception as exc: print(exc); continue
                try: self.ask(line)
                except Exception as exc: print(f"Error: {exc}")
        finally: self.engines.close()

def main(): App().run()
