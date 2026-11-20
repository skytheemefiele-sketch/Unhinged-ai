"""Workspace-scoped tools with explicit safety boundaries."""
from __future__ import annotations
import re, shlex, subprocess, urllib.parse, urllib.request
from pathlib import Path

class ToolError(RuntimeError): pass

class ToolBox:
    def __init__(self, workspace: str | Path, config: dict):
        self.workspace=Path(workspace).expanduser().resolve()
        self.workspace.mkdir(parents=True,exist_ok=True)
        self.config=config

    def _path(self,value: str) -> Path:
        p=(self.workspace/value).resolve()
        if p!=self.workspace and self.workspace not in p.parents:
            raise ToolError("Path escapes the workspace")
        return p

    def file_read(self,path: str) -> str:
        p=self._path(path)
        if not p.is_file(): raise ToolError("File does not exist")
        return p.read_text(encoding="utf-8")

    def file_write(self,path: str,content: str) -> str:
        p=self._path(path); p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(content,encoding="utf-8")
        return f"Wrote {p.relative_to(self.workspace)}"

    def file_patch(self,path: str,old: str,new: str) -> str:
        current=self.file_read(path)
        if old not in current: raise ToolError("Patch target was not found")
        return self.file_write(path,current.replace(old,new,1))

    def file_list(self,path: str=".") -> list[str]:
        p=self._path(path)
        if not p.is_dir(): raise ToolError("Directory does not exist")
        return sorted(str(x.relative_to(self.workspace))+("/" if x.is_dir() else "") for x in p.iterdir())

    def shell_exec(self,command: str,confirm: bool=False) -> dict:
        if not confirm: raise ToolError("Shell execution requires explicit confirmation")
        argv=shlex.split(command)
        if not argv: raise ToolError("Empty command")
        result=subprocess.run(argv,cwd=self.workspace,capture_output=True,text=True,timeout=120)
        return {"returncode":result.returncode,"stdout":result.stdout,"stderr":result.stderr}

    def web_fetch(self,url: str,max_bytes: int=1_000_000) -> str:
        parsed=urllib.parse.urlparse(url)
        if parsed.scheme!="https" or not parsed.hostname: raise ToolError("Only HTTPS URLs are accepted")
        if parsed.hostname in ("localhost","127.0.0.1","::1") or parsed.hostname.endswith(".local"):
            raise ToolError("Local network targets are blocked")
        req=urllib.request.Request(url,headers={"User-Agent":"UnhingedAI/0.1"})
        with urllib.request.urlopen(req,timeout=20) as response: data=response.read(max_bytes+1)
        if len(data)>max_bytes: raise ToolError("Response exceeded size limit")
        return data.decode("utf-8",errors="replace")

    def web_search(self,query: str) -> str:
        url="https://html.duckduckgo.com/html/?q="+urllib.parse.quote(query)
        html=self.web_fetch(url,500_000)
        html=re.sub(r"<(script|style).*?</\1>"," ",html,flags=re.I|re.S)
        html=re.sub(r"<[^>]+>"," ",html)
        return re.sub(r"\s+"," ",html)[:8000]
