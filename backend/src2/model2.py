from src2.kol_condition import condition_kol
from src2.item_repository import load_with_unisex
from src2.ranking import rank_items
import numpy as np
TOPK_PICK = 8

def decide_use_dress(cand, user_vec, kol_vec, margin=0.1):
    if "dress" not in cand or len(cand["dress"]) == 0:
        return False

    best_dress = cand["dress"][0][1]
    best_set = cand["top"][0][1] + cand["bottom"][0][1]

    return best_dress > best_set * (1 + margin)


def model2_recommend(user_vec, kol_clusters, gender="female", beta=0.5):
    kol_vec, kol_weights, ratio = condition_kol(user_vec, kol_clusters)

    style_prior = beta * user_vec + (1 - beta) * kol_vec
    style_prior /= np.linalg.norm(style_prior)

    cand = {}
    roles = ["top", "bottom", "shoes"]
    if gender == "female":
        roles.append("dress")

    for role in roles:
        emb, meta = load_with_unisex(gender, role)
        cand[role] = rank_items(emb, meta, style_prior, TOPK_PICK)


    result = {
        "use_dress": False,
        "items": {}
    }

    if gender == "female":
        use_dress = decide_use_dress(cand, user_vec, kol_vec)
        result["use_dress"] = use_dress

        if use_dress:
            result["items"]["dress"] = cand["dress"]
            result["items"]["shoes"] = cand["shoes"]
        else:
            result["items"]["top"] = cand["top"]
            result["items"]["bottom"] = cand["bottom"]
            result["items"]["shoes"] = cand["shoes"]
    else:
        result["items"] = {
            "top": cand["top"],
            "bottom": cand["bottom"],
            "shoes": cand["shoes"]
        }

    return result
