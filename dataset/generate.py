import os
import sys
import time
import jsons
import json
import argparse
from io import BytesIO
from urllib.request import urlopen
from PIL import Image
import h5py
import numpy as np
import torch
import torchvision.models as models
import torchvision.transforms as transforms
import flickr_api
from flickr_api import Walker, Photo

scoring_path = os.path.abspath("../image_scoring") 
weights_file = os.path.join(scoring_path,"models/MobileNet/weights_mobilenet_aesthetic_0.07.hdf5")
base_model_name = "MobileNet"
sys.path.insert(1, scoring_path)

from src.evaluater.predict import process_samples

from utils import load_credentials, str_time


class GenerateDataset():
    def __init__(self, image_dir=None):
        self._init_feature_extractor()
        self.image_dir=image_dir
        if image_dir != None and not os.path.isdir(image_dir):
            os.makedirs(image_dir)

    def _init_feature_extractor(self):
        scaler = transforms.Resize((224, 224))
        normalizer = transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225])
        to_tensor = transforms.ToTensor()

        model = models.resnet18(pretrained=True)
        layer = model._modules.get("avgpool")
        layer_output_size = 512
        model.eval()
        to_input = lambda img: normalizer(to_tensor(scaler(img))).unsqueeze(0)
        embedding = torch.zeros(1, layer_output_size, 1, 1)
        copy_data = lambda m, i, o: embedding.copy_(o.data)
        h = layer.register_forward_hook(copy_data)

        self.to_input = to_input
        self.embedding = embedding
        self.model = model

    def _get_image(self, url):
        r = urlopen(url)
        s = r.read()
        img = Image.open(BytesIO(s)).convert("RGB")
        return np.void(s), img

    def _get_feature_embedding(self, img):
        x = self.to_input(img)
        self.model(x)
        return self.embedding.squeeze().numpy()

    def _get_metadata(self, p):
        infos = p.getInfo(extras="count_faves")
        infos_ = infos.copy()
        
        # Direct url to photo files of different sizes
        size_labels = ["Square", "Thumbnail", "Small", "Medium", "Medium 640", "Large", "Original"]
        urls = {}
        for size_label in size_labels: 
            try:
                url = p.getPhotoFile(size_label=size_label)
                urls[size_label] = url
            except flickr_api.flickrerrors.FlickrError:
                urls[size_label] = None
        infos_["photo_file_urls"] = urls

        # Extract tags objects
        infos_["tags"] = [tag.__dict__ for tag in infos["tags"]]
        for tag in infos_["tags"]:
            tag.update({'author': {}})

        return jsons.dump(infos_)

    def process(self, p):
        # Metadata as dictionnary
        metadata = self._get_metadata(p)

        # Download image
        url_medium = metadata["photo_file_urls"]["Medium"]
        binary, img = self._get_image(url_medium)
        imid = metadata["id"]
        if self.image_dir != None:
            try: 
                img.save(f"{self.image_dir}/{imid}.jpg", "JPEG")
                print(f"Saved image w/ id {imid}")
            except Exception as e:
                print("whoops, it failed", str(e))
        # Feature extraction
        sample = [{"id":imid, "image":img}]
        print(process_samples(base_model_name, weights_file, sample))
        
        embedding = self._get_feature_embedding(img)

        return metadata, binary, embedding


def generate(api_credentials, city, radius, max_photos, dataset_file, save_dir):
    assert radius > 0, "radius must be positive"
    assert max_photos > 0, "max_photos must be positive"

    cities = {
        "atlanta": (33.7490,-84.3880),
        "paris": (48.8566, 2.3522),
        "sf": (37.773972,-122.431297),
        "nyc": (40.730610,-73.935242),
    }
    city = cities.get(str.lower(city), cities["atlanta"])

    api_key, api_secret = api_credentials
    flickr_api.set_keys(
        api_key=api_key,
        api_secret=api_secret)

    w = Walker(
        Photo.search,
        accuracy=11,
        privacy_filter=1,
        content_type=1,
        media="photos",
        has_geo=1,
        lat=city[0],
        lon=city[1],
        radius=radius,
        tags=["landscape"])

    n_found = len(w)
    n_photos = min(n_found, max_photos)
    batches = max(n_photos // 20, 1)
    print(f"batches: {batches}")
    print(f"Photos found: {n_found}")
    print(f"Photos to be processed in dataset: {n_photos}")

    print("Init dataset generator...", end=" ")
    dataset = GenerateDataset(save_dir)
    print("done.")

    print(f"Start processing photos ({str_time()})")
    dir_path = os.path.dirname(dataset_file)
    os.makedirs(dir_path if dir_path != "" else ".", exist_ok=True) 
    with h5py.File(dataset_file, "w") as f:
        for i, photo in enumerate(w):

            # If photo has already been seen (happens sometimes in Flickr Search)
            if photo.id in f.keys():
                continue

            # Stop if exceed the max number of photos asked
            if i >= max_photos:
                break

            # Due to Flickr limitations on the number of calls per hour on their API
            if i % (3600 // 2) == 0 and i > 0:
                print(f"Paused ({str_time()}) for 1 hour, Flickr API limited to 3600 requests an hour...")
                time.sleep(60 * 60)
                print(f"Resumed! ({str_time()})")

            # Verbose
            if i % batches == 0 or i in [0, n_photos-1]:
                print(f"Process {i+1}/{n_photos}...", end="")

            # Process photo and save in h5 file
            try:
                print(" .", end = '')
                metadata, binary, embedding = dataset.process(photo)
                g = f.create_group(metadata["id"])
                g.create_dataset("binary", data=binary)
                g.create_dataset("embedding", data=embedding)
                g.attrs["metadata"] = json.dumps(metadata)
            except Exception:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                print(exc_type, exc_obj, f"(line {exc_tb.tb_lineno})")

    print(f"Finished ({str_time()}), saved in {dataset_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Explorify dataset generator")
    parser.add_argument('-c', '--city', type=str, default="atlanta", help="City to get pictures from")
    parser.add_argument('-si', '--save-images', type=str, default=None, help="Directory to save images to as JPEG, only use if you want to save images")
    parser.add_argument('-r', '--radius', type=float, default=20.0, help="Radius of the city to cover (in km)")
    parser.add_argument('-m', '--max-photos', type=int, default=int(1e4), help="Maximum number of photos to store")
    parser.add_argument('-d', '--dataset-file', type=str, default="./dataset.h5", help="Path to h5 file to create")
    args = parser.parse_args()
    print(args.save_images)
    flickr_api.enable_cache()
    api_credentials = load_credentials()
    generate(api_credentials, args.city, args.radius, args.max_photos, args.dataset_file, args.save_images)
