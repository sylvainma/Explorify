import os
import json
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.colors import rgb2hex

class GeoJson():

    def __init__(self, dataset, pairs):
        self.dataset = dataset
        self.pairs = pairs
        self._compute_colors()
        self._format_data()

    def _compute_colors(self):
        np.random.seed(1994)
        labels = set([label for _, label in self.pairs if label != -1])
        n_labels = len(labels)#+ sum([1 for _, label in self.pairs if label == -1])
        colors = plt.cm.Spectral(np.linspace(0, 1, n_labels))
        self.colors = {}
        self.colors[-1] = "#000000"
        for label in labels:
            i = np.random.randint(colors.shape[0])
            color = colors[i]
            self.colors[label] = rgb2hex(color[:3])
            colors = np.delete(colors, i, 0)

    def _format_data(self):
        aesthetic_scores = []
        properties = {}
        for id, label in self.pairs:
            metadata, _, _ = self.dataset.get_id(int(id))
            aesthetic_scores.append(float(metadata["aesthetic_score"]))
            properties[id] = {
                "id": metadata["id"],
                "cluster": int(label),
                "lat": float(metadata["location"]["latitude"]),
                "lon": float(metadata["location"]["longitude"]),
                "title": str(metadata["title"]) if ("title" in metadata.keys() and metadata["title"] != "") else "(No title)",
                "url": metadata["photo_file_urls"]["Small"],
                "urls": metadata["photo_file_urls"],
                "tags": [t["text"] for t in metadata["tags"]],
                "aesthetic_score": float(metadata["aesthetic_score"]),
                "rank_score": float(metadata["rank_score"]),
                "likes": metadata["count_faves"],
                "views":metadata["views"],
            }
            properties[id]["marker-color"] = self.colors[label]

        # Aesthetic score rescaling
        min_aes = np.min(aesthetic_scores)
        max_aes = np.max(aesthetic_scores)
        recale_aesthetic_score = lambda s: round((s - min_aes) / (max_aes - min_aes) * 5, 2)
        for id, _ in self.pairs:
            properties[id].update({"aesthetic_score_scaled": recale_aesthetic_score(properties[id]["aesthetic_score"])})

        features = [self._get_feature(properties[id]["lat"], properties[id]["lon"], properties[id]) for id, _ in self.pairs]
        self.data = self._get_feature_collection(features)

    def _get_feature(self, lat, lon, properties):
        return {
            'type': 'Feature',
                'geometry': {
                'type': 'Point',
                'coordinates': [lon, lat]
            },
            'properties': properties
        }

    def _get_feature_collection(self, features):
        return {
            'type': 'FeatureCollection',
            'features': features
        }

    def save_to(self, path):
        with open(path, "w") as f:
            json.dump(self.data, f, indent=4)
