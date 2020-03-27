import os
import json
import h5py


class LoadDataset():
    def __init__(self, dataset_file):
        self.dataset_file = dataset_file
        self.f = h5py.File(self.dataset_file , "r")

    def __del__(self):
        self.f.close()

    def _load(self, p):
        metadata, embedding = p.attrs["metadata"], p[...]
        metadata = json.loads(metadata)
        return metadata, embedding

    def size(self):
        return len(self.f.keys())

    def get_id(self, id):
        p = self.f[str(id)]
        return self._load(p)

    def get(self, keys=None):
        keys = self.f.keys() if keys is None else keys
        for p_id in keys:
            p = self.f[p_id]
            metadata, embedding = self._load(p)
            yield metadata, embedding


if __name__ == "__main__":
    import time
    from .utils import load_credentials
    from .generate import generate
    api_credentials = load_credentials()
    dataset_file = f"./test_to_delete_{int(time.time())}.h5"
    dataset_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), dataset_file)
    generate(api_credentials, "paris", 20, 2, dataset_file)
    try:
        dataset = LoadDataset(dataset_file)
        it = dataset.get()
        metadata, embedding = next(it)
        print(embedding.shape)
        assert type(metadata) == dict, "Metadata should be a python dictionnary"
    except Exception as e:
        raise e
    finally:
        dataset.__del__()
        os.remove(dataset_file)
