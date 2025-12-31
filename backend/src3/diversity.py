# src3/diversity.py
from collections import defaultdict


def _key(meta):
    for k in ("image_path", "path", "filename", "id"):
        if isinstance(meta, dict) and k in meta and meta[k]:
            return meta[k]
    return None


def outfit_item_keys(outfit):
    return [_key(m) for m in outfit.get("items", []) if _key(m) is not None]


def overlap_similarity(a, b):
    """
    Similarity based on item overlap ratio.
    """
    sa = set(outfit_item_keys(a))
    sb = set(outfit_item_keys(b))
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / max(len(sa), len(sb))


def select_diverse_outfits(scored_outfits, k=5, lambda_div=0.55, max_use_per_item=1):
    """
    MMR-like selection + hard cap per item usage.
    - picks high scoring outfits while penalizing similarity with selected ones
    - max_use_per_item=1 makes 5 outfits use more distinct items (your request)
    """
    if not scored_outfits:
        return []

    remaining = sorted(scored_outfits, key=lambda x: x.get("score", -1e9), reverse=True)
    selected = []
    item_count = defaultdict(int)

    while remaining and len(selected) < k:
        best_idx = None
        best_val = -1e9

        for i, cand in enumerate(remaining):
            keys = outfit_item_keys(cand)
            # hard cap per item
            if any(item_count[kk] >= max_use_per_item for kk in keys):
                continue

            base = float(cand.get("score", 0.0))
            if not selected:
                val = base
            else:
                max_sim = max(overlap_similarity(cand, s) for s in selected)
                val = base - lambda_div * max_sim

            if val > best_val:
                best_val = val
                best_idx = i

        if best_idx is None:
            break

        pick = remaining.pop(best_idx)
        selected.append(pick)

        for kk in outfit_item_keys(pick):
            item_count[kk] += 1

    return selected
