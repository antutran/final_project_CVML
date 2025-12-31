# src3/alpha_search.py
import numpy as np
from src3.outfit_scoring import score_outfit


def build_target(user_vec, kol_vec, alpha):
    t = alpha * user_vec + (1 - alpha) * kol_vec
    t = t / (np.linalg.norm(t) + 1e-9)
    return t


def search_best_alpha(user_vec, kol_vec, outfits, alphas, lambda_coh=0.3):
    """
    Alpha* search is model-based (no anti-repeat influence).
    Returns:
      best_alpha, best_outfit (scored dict), alpha_scores [(alpha, best_score_for_alpha)]
    """
    best_alpha = None
    best_score = -1e9
    best_outfit = None
    alpha_scores = []

    for alpha in alphas:
        target = build_target(user_vec, kol_vec, alpha)

        best_for_alpha = -1e9
        for o in outfits:
            bd = score_outfit(o["embs"], target, lambda_coh=lambda_coh)
            if bd["score"] > best_for_alpha:
                best_for_alpha = bd["score"]
            if bd["score"] > best_score:
                best_score = bd["score"]
                best_alpha = alpha
                best_outfit = {**o, **bd}

        alpha_scores.append((float(alpha), float(best_for_alpha)))

    return float(best_alpha), best_outfit, alpha_scores
