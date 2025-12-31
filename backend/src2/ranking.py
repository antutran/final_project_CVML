# ranking.py
import numpy as np

def rank_items(emb, meta, T, k):
    scores = emb @ T
    idxs = np.argsort(scores)[::-1][:k]
    return [(meta[i], float(scores[i])) for i in idxs]
