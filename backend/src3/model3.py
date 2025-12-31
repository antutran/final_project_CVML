from src3.outfit_generator import generate_outfits_from_cand
from src3.alpha_search import build_target
from src3.diversity import select_diverse_outfits
from src3.outfit_scoring import score_outfit


def model3_recommend(
    user_vec,
    kol_vec,
    cand,
    gender,
    alpha_current=0.5,
    pool_per_role=30,
    num_samples=120,
    temperature=0.22,
    lambda_coh=0.3,
    anti_repeat=None,
    lambda_div=0.55,
    max_use_per_item=1,
    final_k=5,
):
    """
    Model3:
    - Generate many outfits
    - Score using fixed alpha
    - Apply anti-repeat
    - Select diverse top-K
    """

    outfits = generate_outfits_from_cand(
        cand,
        gender,
        pool_per_role=pool_per_role,
        num_samples=num_samples,
        temperature=temperature,
        ensure_unique=True,
    )

    target = build_target(user_vec, kol_vec, alpha_current)

    scored = []
    for o in outfits:
        bd = score_outfit(o["embs"], target, lambda_coh=lambda_coh)
        pen = anti_repeat.penalty(o) if anti_repeat else 0.0
        bd["anti_repeat_penalty"] = float(pen)
        bd["score"] = float(bd["score"] - pen)

        scored.append({
            **o,
            **bd,
            "alpha_used": float(alpha_current)
        })

    final = select_diverse_outfits(
        scored_outfits=scored,
        k=final_k,
        lambda_div=lambda_div,
        max_use_per_item=max_use_per_item
    )

    return {
        "alpha_used": float(alpha_current),
        "outfits": final,
        "n_candidates": len(outfits),
    }
