# src3/outfit_generator.py
from itertools import product
import numpy as np

from src2.item_repository import load_with_unisex


def _get_key(meta):
    for k in ("image_path", "path", "filename", "id"):
        if isinstance(meta, dict) and k in meta and meta[k]:
            return meta[k]
    return None


def attach_embeddings(cand, gender):
    """
    cand[role] expected as list of (meta, score) or list of meta dicts
    returns dict role -> list of (meta, score, emb)
    """
    out = {}

    for role, items in cand.items():
        emb_pool, meta_pool = load_with_unisex(gender, role)
        key_to_emb = {}
        for i, m in enumerate(meta_pool):
            k = _get_key(m)
            if k is not None:
                key_to_emb[k] = emb_pool[i]

        triples = []
        for it in items:
            if isinstance(it, tuple) and len(it) >= 2:
                meta, score = it[0], float(it[1])
            else:
                meta, score = it, 0.0

            k = _get_key(meta)
            if k is None or k not in key_to_emb:
                continue

            triples.append((meta, score, key_to_emb[k]))

        out[role] = triples

    return out


def _softmax_weights(scores, temperature=0.20):
    s = np.array(scores, dtype=np.float64)
    if len(s) == 0:
        return s
    if np.allclose(s, s[0]):
        return np.ones_like(s) / max(1, len(s))
    t = max(1e-6, float(temperature))
    z = (s - np.max(s)) / t
    w = np.exp(z)
    w = w / (np.sum(w) + 1e-12)
    return w


def _sample_indices(n, k, weights=None, rng=None):
    rng = rng or np.random.default_rng()
    if n <= 0 or k <= 0:
        return []
    if weights is None:
        return rng.integers(0, n, size=k).tolist()
    w = np.array(weights, dtype=np.float64)
    w = w / (np.sum(w) + 1e-12)
    return rng.choice(np.arange(n), size=k, replace=True, p=w).tolist()


def _make_outfit(items_roles_embs):
    # items_roles_embs: list of (meta, role, emb)
    items = [x[0] for x in items_roles_embs]
    roles = [x[1] for x in items_roles_embs]
    embs = np.stack([x[2] for x in items_roles_embs], axis=0)
    return {"items": items, "roles": roles, "embs": embs}


def _signature(outfit):
    return tuple(sorted([_get_key(m) for m in outfit.get("items", []) if _get_key(m) is not None]))


def generate_outfits_from_cand(
    cand,
    gender,
    pool_per_role=30,
    num_samples=120,
    temperature=0.20,
    ensure_unique=True,
    seed=None,
):
    """
    NEW behavior:
    - Take larger candidate pool per role (pool_per_role, default 30)
    - Generate many outfits by weighted sampling (num_samples, default 120)
    - Optionally ensure unique outfit signatures

    Output outfit dict:
      {items:[meta..], roles:[..], embs: np.array(n_items, dim)}
    """
    rng = np.random.default_rng(seed)
    cand3 = attach_embeddings(cand, gender)

    outfits = []
    seen = set()

    # ---- roles pools
    tops = cand3.get("top", [])[:pool_per_role]
    bottoms = cand3.get("bottom", [])[:pool_per_role]
    shoes = cand3.get("shoes", [])[:pool_per_role]

    # compute weights from candidate scores if present
    w_top = _softmax_weights([x[1] for x in tops], temperature=temperature) if tops else None
    w_bottom = _softmax_weights([x[1] for x in bottoms], temperature=temperature) if bottoms else None
    w_shoes = _softmax_weights([x[1] for x in shoes], temperature=temperature) if shoes else None

    # ---- sample outfits (top-bottom-shoes)
    if tops and bottoms and shoes:
        it = 0
        max_iter = max(num_samples * 4, 200)
        while len(outfits) < num_samples and it < max_iter:
            it += 1
            ti = _sample_indices(len(tops), 1, w_top, rng=rng)[0]
            bi = _sample_indices(len(bottoms), 1, w_bottom, rng=rng)[0]
            si = _sample_indices(len(shoes), 1, w_shoes, rng=rng)[0]

            t = tops[ti]
            b = bottoms[bi]
            s = shoes[si]

            o = _make_outfit([(t[0], "top", t[2]), (b[0], "bottom", b[2]), (s[0], "shoes", s[2])])
            if ensure_unique:
                sig = _signature(o)
                if sig in seen:
                    continue
                seen.add(sig)
            outfits.append(o)

    # ---- optional dress logic (female)
    if gender == "female" and "dress" in cand3 and shoes:
        dresses = cand3.get("dress", [])[:pool_per_role]
        w_dress = _softmax_weights([x[1] for x in dresses], temperature=temperature) if dresses else None

        target_n = max(0, num_samples // 3)
        it = 0
        max_iter = max(target_n * 4, 100)
        while len(outfits) < num_samples + target_n and it < max_iter and dresses:
            it += 1
            di = _sample_indices(len(dresses), 1, w_dress, rng=rng)[0]
            si = _sample_indices(len(shoes), 1, w_shoes, rng=rng)[0]
            d = dresses[di]
            s = shoes[si]
            o = _make_outfit([(d[0], "dress", d[2]), (s[0], "shoes", s[2])])
            if ensure_unique:
                sig = _signature(o)
                if sig in seen:
                    continue
                seen.add(sig)
            outfits.append(o)

    return outfits
