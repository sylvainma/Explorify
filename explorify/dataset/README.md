# Dataset

Use `generate.py` to create an HDFS5 file (.h5) of the images and their metadata. Type `python generate.py --help` for documentation. Example:

```
python generate.py --city paris --radius 15 --max-photos 1000 --dataset-file ../data/paris_1000.h5
python generate.py --city atlanta --radius 30 --max-photos 1000 --dataset-file ../data/atlanta_1000.h5
```

Usage example is given in `visualization.ipynb`