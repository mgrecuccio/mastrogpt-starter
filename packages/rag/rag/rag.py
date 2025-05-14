import os, re, requests as req
import json, socket, traceback, time
import vdb

MODELS = {
  "P": "phi4:14b",
  "L": "llama3.1:8b",
  "M": "mistral:latest"
}

USAGE = """
Start with `@[LPM][<size>][<collection>]` to select the model then add `<size>` sentences from the `<collection>` to the context.
Models: L=llama P=phi4 M=mistral.
You can shorten collection names, it will use the first one starting with the name.
Your query is then passed to the LLM with the sentences for an answer.
Prefix your query with `~` to trigger the image search.
"""

# Pattern: @<model><size><collection> <optional content>
PATTERN = re.compile(r'^@([LPDM]?)(\d*)(\w*)(\s*.*)$')

def parse_query(content):
    res = {
        "model": MODELS["L"],
        "size": 30,
        "collection": "default",
        "content": content
    }

    match = PATTERN.match(content.strip())
    if not match:
        return res
    
    model_key, size_str, collection, content = match.groups()
    
    if model_key in MODELS:
      res["model"] = MODELS[model_key]
    
    try: 
      size = int(size_str)
      res["size"] = size
    except: pass

    if collection != "":
      res["collection"]  = collection

    res["content"] = content.strip()
    
    return res


def streamlines(args, lines):
  sock = args.get("STREAM_HOST")
  port = int(args.get("STREAM_PORT") or "0")
  out = ""
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    if sock:
      s.connect((sock, port))
    try:
      for line in lines:
        time.sleep(0.1)
        msg = {"output": line }
        out += line
        if sock:
          s.sendall(json.dumps(msg).encode("utf-8"))
    except Exception as e:
      traceback.print_exc(e)
      out = str(e)
    if sock:
      s.close()
  return out

def stream(args, lines):
  sock = args.get("STREAM_HOST")
  port = int(args.get("STREAM_PORT") or "0")
  out = ""
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    if sock:
      s.connect((sock, port))
    try:
      for line in lines:
        dec = json.loads(line.decode("utf-8")).get("response")
        msg = {"output": dec }
        out += dec
        if sock:
          s.sendall(json.dumps(msg).encode("utf-8"))
    except Exception as e:
      traceback.print_exc(e)
      out = str(e)
    if sock:
      s.close()
  return out


def llm(args, model, prompt):
  host = args.get("OLLAMA_HOST", os.getenv("OLLAMA_HOST"))
  auth = args.get("AUTH", os.getenv("AUTH"))
  url = f"https://{auth}@{host}/api/generate"

  msg = {
    "model": model,
    "prompt": prompt,
    "stream": True
  }

  lines = req.post(url, json=msg, stream=True).iter_lines()
  return stream(args, lines)

def rag(args):
  res = {}
  out = USAGE
  inp = str(args.get('input', ""))

  if inp != "":
    img_search = inp.startswith('~')
    #sanitize input
    if img_search:
      inp = (inp.lstrip('~') or inp)

    opt = parse_query(inp)
    db = vdb.VectorDB(args, opt["collection"], shorten=True)
    #image rag
    if img_search:
      result_set = db.img_vector_search(opt['content'], limit=opt['size'])
      if len(result_set) > 0 and result_set[0][1] is not None:
        image_url = result_set[0][1]
        out = "This is an image matching your query"
        res['html'] = f"<img src='{image_url}'>"
      else:
        out = "No Image matching your description has been found."
    #text rag
    else:
      if opt['content'] == '':
        db = vdb.VectorDB(args, opt["collection"], shorten=True)
        lines = [f"model={opt['model']}\n", f"size={opt['size']}\n",f"collection={db.collection}\n",f"({",".join(db.collections)})"]
        out = streamlines(args, lines)
      else:
        db = vdb.VectorDB(args, opt["collection"], shorten=True)
        result_set = db.vector_search(opt['content'], limit=opt['size'])
        prompt = ""
        if len(result_set) > 0:
          prompt += "Consider the following text:\n"
          for (w,txt) in result_set:
            prompt += f"{txt}\n"
          prompt += "Answer to the following prompt:\n"

        prompt += f"{opt['content']}"
        out = llm(args, opt['model'], prompt)
        res['streaming'] = True

  res['output'] = out
  return res
