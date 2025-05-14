import bucket

IMG_TYPE = ".jpg"
KEY_PREFIX = "upload/"
TIME_FORMAT = "%Y%m%d-%H%M%S"

import time
def get_img_key():
  return KEY_PREFIX + time.strftime(TIME_FORMAT) + IMG_TYPE

import base64
def store(s3_bucket, img, file_key):
  b64_img = base64.b64decode(img)
  s3_bucket.write(file_key, b64_img)

def get_external_url(s3_bucket, file_key):
  return s3_bucket.exturl(file_key, 3600)

def store_on_s3(args, img):
    s3_bucket = bucket.Bucket(args)
    file_key = get_img_key()
    store(s3_bucket, img, file_key)
    image_s3_path = get_external_url(s3_bucket, file_key)
    return image_s3_path