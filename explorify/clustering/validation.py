import numpy as np
import pandas as pd
from sklearn.metrics import f1_score as scorer

def get_all_annotation(all_files):
    """Merge all annotations files into a single dataframe"""
    li = []
    for filename in all_files:
        df = pd.read_csv(filename)
        li.append(df)
    df = pd.concat(li, axis=0, ignore_index=True)
    # If duplicates, keep the most voted label
    df = df.groupby(["id1","id2"]).agg(lambda x: x.value_counts().index[0]).reset_index()
    return df

def score_A(labels, idx, val_set):
    """
    Strategy A: Loop over the annotations.

    Pros:
        Correspond to a traditional classification performance score.
        Reward clustering that excatly matches human annotations.
    Cons:
        Penalize even if clusters themselves are homogeneous.
        Highly dependent on the size and quality of annotations.
    """
    label_lookup = {int(idx[i]): label for i, label in enumerate(labels)}
    y_true, y_pred = [], []
    for id1, id2, together in val_set:
        # Check if id1 and id2 have been predicted
        label_of_id1 = label_lookup.get(id1, None)
        label_of_id2 = label_lookup.get(id2, None)
        if label_of_id1 is None or label_of_id2 is None:
            continue

        # Check if they are in the same cluster, except if they are in -1
        y_true.append(together)
        if label_of_id1 == label_of_id2 and label_of_id1 != -1:
            y_pred.append(1)
        else:
            y_pred.append(0)

    sA = scorer(y_true, y_pred)
    return sA

def score_B(labels, idx, val_set):
    """
    Strategy B: Loop over the predictions.

    Pros:
        Focus on the correctness of the clusters themselves.
        Reward homogeneous clusters.
    Cons:
        Ignore images that should have been clustered together but were not.
        Rewards smaller clusters with few errors in them.
    """
    y_true, y_pred = [], []
    for label in set(labels):
        if label == -1: continue
        label_idx = [idx[i] for i in range(labels.shape[0]) if labels[i] == label]
        for i in range(len(label_idx)-1):
            for j in range(i, len(label_idx)):
                pair = list(filter(lambda r: \
                        (r[0] == int(label_idx[i]) and r[1] == int(label_idx[j])) or \
                        (r[0] == int(label_idx[j]) and r[1] == int(label_idx[i]))
                , val_set))
                if len(pair) == 0:
                    continue
                else:
                    together = pair.pop()[2]
                    y_true.append(1)
                    y_pred.append(together)
    
    sB = scorer(y_true, y_pred)
    return sB

def score(labels, idx, val_set):
    """
    Trade-off between classification performance and cluster homogeneity.
    """
    sA = score_A(labels, idx, val_set)
    sB = score_B(labels, idx, val_set)
    #s = 0.5 * sA + 0.5 * sB
    s = 2*(sA*sB)/(sA+sB)
    return s