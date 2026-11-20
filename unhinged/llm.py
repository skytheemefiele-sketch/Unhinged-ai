"""OpenAI-compatible chat client using only the Python standard library."""
import json, urllib.request, urllib.error

def chat(base_url: str, model: str, messages: list[dict], api_key: str = "", timeout: int = 120) -> str:
    url=base_url.rstrip("/")+"/chat/completions"
    payload=json.dumps({"model":model,"messages":messages,"temperature":0.6}).encode()
    headers={"Content-Type":"application/json"}
    if api_key: headers["Authorization"]="Bearer "+api_key
    req=urllib.request.Request(url,data=payload,headers=headers,method="POST")
    try:
        with urllib.request.urlopen(req,timeout=timeout) as res: data=json.loads(res.read())
    except urllib.error.HTTPError as exc:
        detail=exc.read(2000).decode(errors="replace")
        raise RuntimeError(f"LLM endpoint returned HTTP {exc.code}: {detail}") from exc
    try: return data["choices"][0]["message"]["content"]
    except (KeyError,IndexError,TypeError) as exc: raise RuntimeError("Unexpected OpenAI-compatible response shape") from exc
