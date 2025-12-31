# item_repository.py
import json
import numpy as np
from pathlib import Path
from src2.config import ITEM_EMB_ROOT

ROOT = Path(ITEM_EMB_ROOT)

def load_pool(gender, category):
    emb = np.load(ROOT / gender / category / "emb_30d.npy")
    with open(ROOT / gender / category / "meta.json", "r") as f:
        meta = json.load(f)
    
    # No path conversion needed - meta.json already has correct Mac paths
    # pointing to ITEMS_CLEAN directory
    
    return emb, meta


def load_with_unisex(gender, category):
    emb1, meta1 = load_pool(gender, category)

    try:
        emb2, meta2 = load_pool("unisex", category)
        return np.vstack([emb1, emb2]), meta1 + meta2
    except FileNotFoundError:
        # unisex chưa có data → bỏ qua
        return emb1, meta1
