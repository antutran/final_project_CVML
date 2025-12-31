#!/usr/bin/env python3
"""Check embedding and metadata counts"""
import numpy as np
import json
from pathlib import Path

ITEM_EMB_ROOT = Path("/Users/tuantran/Downloads/CVML/backend/ITEM_EMB")

CATEGORIES = {
    "female": ["top", "bottom", "shoes", "dress"],
    "male": ["top", "bottom", "shoes"],
    "unisex": ["top", "bottom", "shoes"],
}

print("Checking embeddings vs metadata counts:\n")

mismatch_found = False

for gender in CATEGORIES.keys():
    for category in CATEGORIES[gender]:
        emb_file = ITEM_EMB_ROOT / gender / category / "emb_30d.npy"
        meta_file = ITEM_EMB_ROOT / gender / category / "meta.json"
        
        if not emb_file.exists():
            print(f"⚠️  {gender}/{category}: emb file not found")
            continue
            
        if not meta_file.exists():
            print(f"⚠️  {gender}/{category}: meta file not found")
            continue
        
        emb = np.load(emb_file)
        with open(meta_file) as f:
            meta = json.load(f)
        
        emb_count = emb.shape[0]
        meta_count = len(meta)
        
        status = "✅" if emb_count == meta_count else "❌"
        print(f"{status} {gender:6s}/{category:6s}: emb={emb_count:3d}, meta={meta_count:3d}")
        
        if emb_count != meta_count:
            mismatch_found = True

if mismatch_found:
    print("\n❌ Found mismatches!")
else:
    print("\n✅ All counts match!")
