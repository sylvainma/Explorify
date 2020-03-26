import os
import time
from io import BytesIO
from urllib.request import urlopen
from PIL import Image


def str_time():
    return time.strftime("%H:%M:%S", time.localtime())


def load_credentials():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".flickr_keys.txt")
    with open(path, "r") as f:
        line = f.readline()
        api_key, api_secret = line.split(" ")
        return api_key, api_secret


def get_photo(p, size_label="Medium"):
    url = p.getPhotoFile(size_label=size_label)
    r = urlopen(url)
    b = BytesIO(r.read())
    return Image.open(b)
