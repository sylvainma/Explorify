import numpy as np
from sklearn.metrics.pairwise import haversine_distances, cosine_distances, euclidean_distances

def compute_distances(A, dist_method):
    n, _ = A.shape
    d = np.zeros((n,n))
    for i in range(n):
        for j in range(i, n):
            d[i,j] = dist_method(np.expand_dims(A[i], axis=0), np.expand_dims(A[j], axis=0)).item()
    d += d.T
    assert d.shape[0] == A.shape[0]
    assert d.shape[0] == d.shape[1]
    return d

def dist_geo(X):
    """Geo distance. X and Y should be lat/lon of shape (n_sample, 2)"""
    X_in_radians = np.radians(X)
    dist = haversine_distances(X_in_radians)
    dist *= 6371.0
    return dist

def dist_img(X):
    """Photo distance. X should be the feature representations of shape (n_sample, dim_embeddings)"""
    return euclidean_distances(X)

def dist_tag(X):
    """Tags distance. X should be the vectorized representation of tags of shape (n_sample, dim_tags)"""
    return cosine_distances(X)

if __name__ == "__main__":
    # dist_geo test
    bsas = [-34.83333, -58.5166646]
    paris = [49.0083899664, 2.53844117956]
    dummy = [2, 2]
    dist = dist_geo(np.asarray([bsas, paris, dummy])).astype(np.int32)
    assert dist.shape[0] == 3
    assert dist.shape[1] == 3
    assert dist[0,1] == 11099
    assert dist[0,1] == dist[1,0]
    assert np.diag(dist).sum() == 0