"""Tolerant extraction of JSON tool-call objects from model output."""
import json, re

def extract_tool_calls(text: str) -> list[dict]:
    candidates=[]
    for block in re.findall(r"```(?:json)?\\s*(.*?)```",text,re.I|re.S): candidates.append(block)
    candidates.append(text)
    calls=[]
    for candidate in candidates:
        decoder=json.JSONDecoder()
        for match in re.finditer(r"\\{",candidate):
            try:
                obj,end=decoder.raw_decode(candidate[match.start():])
                if isinstance(obj,dict) and isinstance(obj.get("tool"),str):
                    calls.append(obj)
            except json.JSONDecodeError: continue
    return calls
