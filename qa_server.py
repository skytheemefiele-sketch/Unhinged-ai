"""Minimal, non-sensitive HTTP health endpoint for Render smoke tests."""
from http.server import BaseHTTPRequestHandler, HTTPServer
import json, os

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path not in ("/","/healthz"):
            self.send_error(404); return
        body=json.dumps({"status":"ok","service":"unhinged-ai-qa","health_check":True}).encode()
        self.send_response(200); self.send_header("Content-Type","application/json")
        self.send_header("Content-Length",str(len(body))); self.end_headers(); self.wfile.write(body)
    def log_message(self,fmt,*args):
        # Avoid logging request query strings or user content.
        print("QA HTTP",self.command,self.path.split("?")[0],args[1] if len(args)>1 else "")

if __name__=="__main__":
    port=int(os.environ.get("PORT","10000"))
    HTTPServer(("0.0.0.0",port),Handler).serve_forever()
