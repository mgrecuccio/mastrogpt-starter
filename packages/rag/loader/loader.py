import vdb
import ast
import s3_utils, vision_utils

USAGE = f"""Welcome to the Vector DB Loader.
Write text to insert in the DB. 
Use `@[<coll>]` to select/create a collection and show the collections.
Use `*<string>` to vector search the <string> in the DB.
Use `#<limit>`  to change the limit of searches.
Use `!<substr>` to remove text with `<substr>` in collection.
Use `!![<collection>]` to remove `<collection>` (default current) and switch to default.
Use `+img` to upload an image.
"""

UPLOAD_IMG_USAGE = "Please upload a picture. It will embedded and stored in Vector DB."
UPLOAD_IMG_FORM = [
  {
    "label": "Upload a picture",
    "name": "pic",
    "required": "true",
    "type": "file"
  },
]

def get_img(inp):
  form_dic = ast.literal_eval(inp)
  img = form_dic.get("form", {}).get("pic", "")
  return img

def loader(args):
  resp = {}
  collection = "default"
  limit = 30
  sp = args.get("state", "").split(":")
  if len(sp) > 0 and len(sp[0]) > 0:
    collection = sp[0]
  if len(sp) > 1:
    try:
      limit = int(sp[1])
    except: pass
  print(collection, limit)

  out = f"{USAGE}Current collection is {collection} with limit {limit}"
  db = vdb.VectorDB(args, collection)
  inp = str(args.get('input', ""))

  # select collection
  if inp.startswith("@"):
    out = ""
    if len(inp) > 1:
       collection = inp[1:]
       out = f"Switched to {collection}.\n"
    out += db.setup(collection)
  # upload an image
  elif inp.startswith('+img'):
    out = UPLOAD_IMG_USAGE
    resp['form'] = UPLOAD_IMG_FORM
  # set size of search
  elif inp.startswith("#"):
    try: 
       limit = int(inp[1:])
    except: pass
    out = f"Search limit is now {limit}.\n"
  # run a query
  elif inp.startswith("*"):
    search = inp[1:]
    if search == "":
      search = " "
    res = db.vector_search(search, limit=limit)
    if len(res) > 0:
      out = f"Found:\n"
      for i in res:
        out += f"({i[0]:.2f}) {i[1]}\n"
    else:
      out = "Not found"
  # remove a collection
  elif inp.startswith("!!"):
    if len(inp) > 2:
      collection = inp[2:].strip()
    out = db.destroy(collection)
    collection = "default"
  # remove content
  elif inp.startswith("!"):
    count = db.remove_by_substring(inp[1:])
    out = f"Deleted {count} records."    
  elif inp != '':
    if "pic" in inp and "form" in inp:
      out = "Inserted image: "
      img = get_img(inp)
      #store image in S3
      image_s3_path = s3_utils.store_on_s3(args, img)
      # Process image with vision LLM
      text = vision_utils.decode_img(args, img)
      # persist embedded image in Milvus
      res = db.insert(text, image_s3_path)
      out += "\n".join([str(x) for x in res.get("ids", [])])
      out += "\n"
    else: 
      out = "Inserted "
      lines = [inp]
      if args.get("options","") == "splitlines":
        lines = inp.split("\n")
      for line in lines:
        if line == '': continue
        res = db.insert(line)
        out += "\n".join([str(x) for x in res.get("ids", [])])
        out += "\n"

  resp['output'] = out
  resp['state'] = f"{collection}:{limit}"
  return resp
  
