import vision
import sys ; sys.path.append("packages/vision/store")
import bucket

USAGE = "Please upload a picture and I will tell you what I see"
FORM = [
  {
    "label": "any pics?",
    "name": "pic",
    "required": "true",
    "type": "file"
  },
]

KEY_PREFIX = "upload/"
TIME_FORMAT = "%Y%m%d-%H%M%S"
FILE_TYPE = ".jpg"

def get_file_key():
  import time
  return KEY_PREFIX + time.strftime(TIME_FORMAT) + FILE_TYPE


import base64
def store(my_bucket, img):
  file_key = get_file_key()
  b64_img = base64.b64decode(img)
  my_bucket.write(file_key, b64_img)
  return file_key


def get_external_url(my_bucket, file_key):
  return my_bucket.exturl(file_key, 3600)


def form(args):
  res = {}
  out = USAGE
  inp = args.get("input", "")

  if type(inp) is dict and "form" in inp:
    img = inp.get("form", {}).get("pic", "")
    my_bucket = bucket.Bucket(args)
    file_key = store(my_bucket, img)
    url = get_external_url(my_bucket, file_key)
    vis = vision.Vision(args)
    out = vis.decode(img)
    #res['html'] = f'<img src="data:image/png;base64,{img}">'
    res['html'] = f"<img src='{url}'>"
    
  res['form'] = FORM
  res['output'] = out
  return res
