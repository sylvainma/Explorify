import os
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

from utils import load_credentials, str_time


class GenerateDataset():
    def __init__(self):
        self._init_feature_extractor()

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
        b = BytesIO(r.read())
        return Image.open(b)

    def _get_feature_embedding(self, img):
        x = self.to_input(img)
        self.model(x)
        return self.embedding.squeeze().numpy()

    def _get_metadata(self, info):
        return jsons.dump(info)

    def process(self, p):
        # Metadata as dictionnary
        metadata = self._get_metadata(p.getInfo())

        # Download image
        img = self._get_image(p.getPhotoFile())
        
        # Feature extraction
        embedding = self._get_feature_embedding(img)

        return metadata, embedding


def generate(api_credentials, city, radius, max_photos, dataset_file):
    assert radius > 0, "radius must be positive"
    assert max_photos > 0, "max_photos must be positive"

    cities = {
        "atlanta": (33.7490, 84.3880),
        "paris": (48.8566, 2.3522)
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
    print(f"Photos found: {n_found}")
    print(f"Photos to be processed in dataset: {n_photos}")

    print("Init dataset generator...", end=" ")
    dataset = GenerateDataset()
    print("done.")

    print(f"Start processing photos ({str_time()})")
    dir_path = os.path.dirname(dataset_file)
    os.makedirs(dir_path if dir_path != "" else ".", exist_ok=True) 
    with h5py.File(dataset_file, "w") as f:
        for i, photo in enumerate(w):
            if photo.id in f.keys():
                continue
            if i >= max_photos:
                break
            if i % (3600 // 2) == 0 and i > 0:
                print(f"Paused ({str_time()}) for 1 hour, Flickr API limited to 3600 requests an hour...")
                time.sleep(60 * 60)
                print(f"Resumed! ({str_time()})")
            if i % batches == 0 or i in [0, n_photos-1]:
                print(f"Process {i}/{n_photos}...")
            try:
                # Save in h5 file
                metadata, embedding = dataset.process(photo)
                d = f.create_dataset(metadata["id"], data=embedding)
                d.attrs["metadata"] = json.dumps(metadata)
            except Exception as e:
                print(e)

    print(f"Finished ({str_time()}), saved in {dataset_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Explorify dataset generator")
    parser.add_argument('-c', '--city', type=str, default="atlanta", help="City to get pictures from")
    parser.add_argument('-r', '--radius', type=float, default=20.0, help="Radius of the city to cover (in km)")
    parser.add_argument('-m', '--max-photos', type=int, default=int(1e4), help="Maximum number of pictures to store")
    parser.add_argument('-d', '--dataset-file', type=str, default="./dataset.h5", help="Path to h5 file to create")
    args = parser.parse_args()

    api_credentials = load_credentials()
    generate(api_credentials, args.city, args.radius, args.max_photos, args.dataset_file)
