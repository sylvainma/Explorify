import numpy as np
import pandas as pd
from PIL import Image

import torch
from sklearn.cluster import DBSCAN
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score, calinski_harabasz_score
from sklearn.metrics.pairwise import cosine_similarity
from .embedding import forward
from .tags import vectorizer
from .distances import dist_geo, dist_img, dist_tag


class MultiFeatureDBSCAN():
    def __init__(self, dataset, model, weights, max_data=100, eps=0.1, min_samples=5, verbose=True):
        """DBSCAN Clustering of Flickr photographs using a combination of geographic data,
            visual representation and tags information.
        
        Inputs:
        - dataset: HDFS5 data loader 
        - model: pytorch model to infer a vector embedding from raw images
        - weights: in order (alpha, beta, gamma) the weights for the final distance space
        - max_data: maximum data to fetch from dataset and use as training set
        - eps: DBSCAN, should be in [0,1] since distances are normalized in [0,1]
        - min_samples: DBSCAN, minimum number of samples around for core samples
        """
        self.dataset = dataset
        self.model = model
        self.alpha, self.beta, self.gamma = weights
        assert self.alpha + self.beta + self.gamma == 1
        self.max_data = max_data
        self.eps = eps
        assert eps >= 0
        assert eps <= 1
        self.min_samples = min_samples
        assert min_samples >= 0
        self.verbose = verbose

    def _normalize_dist_matrix(self, dist_matrix):
        """MinMax scaling of distances in [0,1]"""
        return (dist_matrix - dist_matrix.min()) / (dist_matrix.max() - dist_matrix.min())

    def get_data(self, dataset, max_data):
        """Get raw data from the HDFS5 file"""
        it = dataset.get()
        idx, locations, images, tags = [], [], [], []
        for i, row in enumerate(it):
            if i >= max_data: break
            metadata, image, _ = row
            # ID
            idx.append(metadata["id"])
            # Location
            lat = float(metadata["location"]["latitude"])
            lon = float(metadata["location"]["longitude"])
            locations.append([lat, lon])
            # Images
            images.append(image)
            # Tags
            t = " ".join([tag["text"] for tag in metadata["tags"]])
            tags.append(t)

        assert len(idx) == len(locations)
        assert len(idx) == len(images)
        assert len(idx) == len(tags)
        assert len(idx) <= max_data
        return idx, locations, images, tags

    def fit(self):
        """Training pipeline: from loading the data, preprocessing it and building the clusters."""
        # Get features from dataset
        if self.verbose: print("Get data from hdfs5 file...")
        idx, locations, images, tags = self.get_data(self.dataset, max_data=self.max_data)

        # Batch forward for embeddings
        if self.verbose: print("Images to embeddings...")
        self.model.eval()
        with torch.no_grad():
            embeddings = forward(self.model, images)
        embeddings = PCA(n_components=min(512, min(*embeddings.shape))).fit_transform(embeddings)

        # Batch TF-IDF for tags
        if self.verbose: print("Vectorization of tags...")
        tags = vectorizer([t.split(" ") for t in tags]).todense()
        tags = PCA(n_components=min(512, min(*tags.shape))).fit_transform(tags)

        # Convert to numpy arrays
        X_locations = np.asarray(locations)
        X_embeddings = embeddings
        X_tags = tags
        if self.verbose: print(f"Final training set: {X_locations.shape} {X_embeddings.shape} {X_tags.shape}")

        # Build each distance matrix
        if self.verbose: print("Compute distance matrix of locations...")
        dist_matrix_geo = self._normalize_dist_matrix(dist_geo(X_locations))
        if self.verbose: print("Compute distance matrix of embeddings...")
        dist_matrix_img = self._normalize_dist_matrix(dist_img(X_embeddings))
        if self.verbose: print("Compute distance matrix of tags...")
        dist_matrix_tag = self._normalize_dist_matrix(dist_tag(X_tags))

        # Weighted combination
        dist_matrix = self.alpha * dist_matrix_geo
        dist_matrix += self.beta * dist_matrix_img
        dist_matrix += self.gamma * dist_matrix_tag
        assert dist_matrix.shape[0] == dist_matrix.shape[1]
        assert dist_matrix.shape[0] == len(idx)
        if self.verbose: print("dist_matrix:", 
            dist_matrix.min(), f"{dist_matrix.mean()}+-{dist_matrix.std()}", dist_matrix.max())

        # DBSCAN clustering
        if self.verbose: print("Training DBSCAN...")
        db = DBSCAN(eps=self.eps, min_samples=self.min_samples, metric="precomputed", n_jobs=-1)
        db.fit_predict(dist_matrix)
        labels = db.labels_
        clusters, counts = np.unique(labels, return_counts=True)

        # Stats
        if self.verbose:
            print("Result:", f"{len(clusters)-1} clusters")
            if len(clusters) > 1:
                print("Counts:", counts[1:].min(), f"{counts[1:].mean()}+-{counts[1:].std()}", counts[1:].max())

        # Logs
        self.idx = idx
        self.X_locations = X_locations
        self.X_embeddings = X_embeddings
        self.X_tags = X_tags
        self.dist_matrix_geo = dist_matrix_geo
        self.dist_matrix_img = dist_matrix_img
        self.dist_matrix_tag = dist_matrix_tag
        self.dist_matrix = dist_matrix
        self.db = db
        self.labels = labels

    def results(self):
        """Performance metrics"""
        # silhouette_score:
        # - Between 0 and 1, higher is better
        # calinski_harabasz_score:
        # - The score is higher when clusters are dense and well separated, which relates to a standard concept of a cluster.
        if len(set(self.labels)) < 2: 
            sil = np.nan
            cha = np.nan
        else: 
            sil = silhouette_score(self.dist_matrix, self.labels, metric="precomputed")
            cha = calinski_harabasz_score(self.dist_matrix, self.labels)

        # Clusters similarities: embeddings
        cluster_embeddings_similarities = {}
        for label in set(self.labels):
            if label == -1: continue
            cluster_embeddings = [self.X_embeddings[i] for i in range(self.labels.shape[0]) if self.labels[i] == label]
            cluster_embeddings = np.vstack(cluster_embeddings)
            cluster_embeddings_similarities[label] = cosine_similarity(cluster_embeddings).mean()
        cluster_embeddings_similarities

        # Clusters similarities: tags
        cluster_tags_similarities = {}
        for label in set(self.labels):
            if label == -1: continue
            cluster_tags = [self.X_tags[i] for i in range(self.labels.shape[0]) if self.labels[i] == label]
            cluster_tags = np.vstack(cluster_tags)
            cluster_tags_similarities[label] = cosine_similarity(cluster_tags).mean()
        cluster_tags_similarities

        return {
            "n_clusters": len(set(self.labels)) - 1,
            "sil": sil,
            "cha": cha,
            "embeddings_sims": cluster_embeddings_similarities,
            "tags_sims": cluster_tags_similarities
        }


if __name__ == "__main__":
    import sys
    sys.path.append("..")
    from embedding import VGG16
    from dataset.load import LoadDataset
    params = {
        "dataset": LoadDataset("../data/paris_1000_test.h5"),
        "model": VGG16(-5),
        "weights": (0.33, 0.33, 1-2*0.33),
        "max_data": 10,
        "eps": 0.1,
        "min_samples": 1
    }
    model = MultiFeatureDBSCAN(**params)
    model.fit()
    