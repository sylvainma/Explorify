import sys
import os
import argparse
from itertools import product
import datetime
import glob
import numpy as np
import pandas as pd
from tabulate import tabulate
from tqdm import tqdm

from dataset.load import LoadDataset
from clustering.dbscan import MultiFeatureDBSCAN
from clustering.embedding import WSL, VGG16
from clustering.validation import get_all_annotation, score


def main(args):
    """Clustering gridsearch"""

    # Common attributes
    print("Initializing gridsearch space...")
    cnn_model = VGG16(-5)
    dataset = LoadDataset("./data/paris_1000.h5")
    max_data = 500
    val_set = get_all_annotation(glob.glob("data/annotations/annotations_*.csv")).values.tolist()

    # Define gridsearch space
    grid_params = [
        {"dataset": dataset, "model": cnn_model, "weights": (1.0, 0.0, 0.0), "max_data": max_data, "verbose": False},
        {"dataset": dataset, "model": cnn_model, "weights": (0.0, 1.0, 0.0), "max_data": max_data, "verbose": False},
        {"dataset": dataset, "model": cnn_model, "weights": (0.0, 0.0, 1.0), "max_data": max_data, "verbose": False},
        {"dataset": dataset, "model": cnn_model, "weights": (0.33, 0.33, 1-2*0.33), "max_data": max_data, "verbose": False},
    ]
    search_space = list(product(grid_params, np.arange(0.01, 0.20, 0.02), np.arange(2, 10, 1)))
    print(f"Space length: {len(search_space)}")

    # Start to explore search space
    print(f"Starting gridsearch")
    results = pd.DataFrame()
    for candidate in tqdm(search_space, total=len(search_space)):
        try:
            params, eps, min_samples = candidate
            params.update({"eps": eps, "min_samples": min_samples})
            model = MultiFeatureDBSCAN(**params)
            model.fit()
            metrics = model.results()
            metrics.update({"score": score(model.labels, model.idx, val_set)})
            metrics.update(params)
            results = results.append(metrics, ignore_index=True)
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, f"(line {exc_tb.tb_lineno})")
    print("Done.")

    # Summary table of best performances for each weights configuration
    results["embeddings_sims_mean"] = results["embeddings_sims"].apply(lambda sims: np.mean([v for _,v in sims.items()]))
    results["tags_sims_mean"] = results["tags_sims"].apply(lambda sims: np.mean([v for _,v in sims.items()]))
    best = results\
        .sort_values(by=["score", "n_clusters", "sil", "embeddings_sims_mean", "tags_sims_mean"], ascending=False)\
        .groupby("weights").head(1)
    best = best[["weights", "n_clusters", "score"]]
    print(tabulate(best, headers='keys', tablefmt='psql', showindex=False))

    # Save results to a csv in logs directory
    os.makedirs(args.logs, exist_ok=True)
    results_path = os.path.join(args.logs, "results.csv")
    results.to_csv(results_path, index=False)
    print(f"Results saved in {results_path}")
    best_path = os.path.join(args.logs, "best.csv")
    best.to_csv(best_path, index=False)
    print(f"Best saved in {best_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Explorify clustering gridsearch")
    parser.add_argument('-l', '--logs', type=str, default=f"logs/{int(datetime.datetime.now().timestamp())}", help="Path to logs directory")
    args = parser.parse_args()
    main(args)
