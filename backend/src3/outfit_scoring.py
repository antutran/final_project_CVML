import numpy as np


def cosine(a, b):
    return float(np.dot(a, b) / ((np.linalg.norm(a) + 1e-9) * (np.linalg.norm(b) + 1e-9)))


def coherence_score(embs):
    n = len(embs)
    if n < 2:
        return 0.0
    sims = []
    for i in range(n):
        for j in range(i + 1, n):
            sims.append(cosine(embs[i], embs[j]))
    return float(np.mean(sims))


def score_outfit(embs, target_vec, lambda_coh=0.3):
    mean_emb = np.mean(embs, axis=0)
    style_fit = cosine(mean_emb, target_vec)
    coh = coherence_score(embs)
    score = style_fit + lambda_coh * coh
    return {
        "style_fit": float(style_fit),
        "coherence": float(coh),
        "score": float(score),
    }
