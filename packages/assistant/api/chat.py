import os
import openai

MODEL = "llama3.1:8b"
ROLE = "system:You are an helpful assistant."

import socket, traceback, json
def stream(args, lines):
    sock = args.get("STREAM_HOST")
    port = int(args.get("STREAM_PORT"))
    out = ""

    with(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.connect((sock, port))

        try:
            for line in lines:
                msg = {"output": line.choices[0].delta.content }
                s.sendall(json.dumps(msg).encode("utf-8"))
        except Exception as e:
            traceback.print_exc(e)
            out = str(e)
    return out


class Chat:
    def __init__(self, args):
        
        host = args.get("OLLAMA_HOST", os.getenv("OLLAMA_HOST"))
        api_key = args.get("AUTH", os.getenv("AUTH"))
        base_url = f"https://{api_key}@{host}/v1"
        
        self.client = openai.OpenAI(
            base_url = base_url,
            api_key = api_key,
        )
        
        self.messages = []
        self.add(ROLE)    
        self.args=args
        
    def add(self, msg):
        [role, content] = msg.split(":", maxsplit=1)
        self.messages.append({
            "role": role,
            "content": content,
        })
    
    def complete(self):
    
        res = self.client.chat.completions.create(
            model=MODEL,
            messages=self.messages,
            stream=True
        )
        try: 
            out = stream(self.args, res)

            # persists the history
            self.add(f"assistant:{out}")
        except:
            out =  "error"
        return out
    
