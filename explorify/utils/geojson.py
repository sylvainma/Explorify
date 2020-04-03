import os
import json
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.colors import rgb2hex

class GeoJson():

    def _get_geojson(self, features):
        return {
            'type': 'FeatureCollection',
            'features': features
        }

    def _get_features(self, cols, row, lng, lat, color):
        properties = {k: str(v) for k,v in zip(cols, [row[col] for col in cols])}
        properties['marker-color'] = rgb2hex(color[:3])
        return {
            'type': 'Feature',
                'geometry': {
                'type': 'Point',
                'coordinates': [row[lat], row[lng]]
            },
            'properties': properties
        }

    def to_geojson(self, df, groupby, lat, lng, cols):

        clusters = df.groupby(groupby)

        features = []
        colors = plt.cm.Spectral(np.linspace(0, 1, len(clusters)))
        for _, group in clusters:
            i = np.random.randint(colors.shape[0])
            color = colors[i]
            group.apply(lambda row: features.append(self._get_features(
                cols, row, lat, lng, color)
            ), axis=1)
            colors = np.delete(colors, i, 0)

        self.data = self._get_geojson(features)
        return self

    def save_to(self, path):
        with open(path, "w") as f:
            json.dump(self.data, f, indent = 4)