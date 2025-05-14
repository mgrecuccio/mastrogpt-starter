import os
import requests
import json

VISION_MODEL = "llava:7b"

def collect(lines):
  out = ""
  for line in lines:
    chunk = json.loads(line.decode("UTF-8"))
    out +=  chunk.get("message", {}).get("content", "")
  return out

def decode_img(args, img):
   host = args.get("OLLAMA_HOST", os.getenv("OLLAMA_HOST"))
   auth = args.get("OLLAMA_TOKEN", os.getenv("AUTH"))
   url = f"https://{auth}@{host}/api/chat"
   msg = {
    "model": VISION_MODEL,
    "messages": [ {
        "role": "user",
        "content": "what is in this image?",
        "images": [img]
        }]
    }
   img_chunks = requests.post(url, json=msg, stream=True).iter_lines()
   text=collect(img_chunks)
   return text