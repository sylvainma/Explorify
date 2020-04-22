# Explorify - Backend
```
.
├── annotation      # Annotation tool
├── clustering      # Clustering models
├── data            # Dataset storage
├── dataset         # Dataset download
├── scoring         # Scoring models
├── utils           # Misc utils
└── webapp-dev      # Clustering viewer
```

## Getting started
First, install backend dependencies with:
```
pip install -r requirements.txt
```

Second, add in a file `.mongodb.txt` the mondb url to the database that hosts the geojson data.

Third, make sure h5 files are present in `data` folder or generate one with `datasets/generate.py`. See `datasets/README.md` for instructions.

Then use `clustering/clustering.ipynb` to train the clustering model and generate the `<city>.geojson`.

## Gridsearch of best parameters
To perform a gridsearch clustering, run:
```
python clustering.py
```
In the generated `logs` directory, the best hyperparameters will be saved in csv files. You can then use these hyperparameters to train the final model and generate the `<city>.geojson` files using `clustering/clustering.ipynb`.