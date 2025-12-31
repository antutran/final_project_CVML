import numpy as np

def condition_kol(user_vec, kol_clusters, tau=0.15, temperature=1.0):
    """
    Hybrid KOL conditioning:
    - Hard if confident
    - Soft if ambiguous
    """
    dists = np.linalg.norm(kol_clusters - user_vec[None, :], axis=1)

    # Sort distances
    idx = np.argsort(dists)
    d1, d2 = dists[idx[0]], dists[idx[1]]

    # Relative margin
    ratio = abs(d2 - d1) / max(d1, d2)

    if ratio >= tau:
        # confident → hard
        kol_vec = kol_clusters[idx[0]]
        weights = np.zeros(len(kol_clusters))
        weights[idx[0]] = 1.0
    else:
        # ambiguous → soft
        w = np.exp(-dists / temperature)
        w = w / w.sum()
        kol_vec = (w[:, None] * kol_clusters).sum(axis=0)
        kol_vec /= np.linalg.norm(kol_vec)
        weights = w

    return kol_vec, weights, ratio
