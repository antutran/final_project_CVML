#!/usr/bin/env python3
"""
Generate meta.json files for ITEMS_CLEAN directory.
This creates the metadata structure needed for the demo to work with ITEMS_CLEAN images.
IMPORTANT: Only includes items up to the number of embeddings available.
"""

import json
import numpy as np
from pathlib import Path

ITEMS_CLEAN_ROOT = Path("/Users/tuantran/Downloads/CVML/dataset/ITEMS_CLEAN")
ITEM_EMB_ROOT = Path("/Users/tuantran/Downloads/CVML/backend/ITEM_EMB")

CATEGORIES = {
    "female": ["top", "bottom", "shoes", "dress"],
    "male": ["top", "bottom", "shoes"],
    "unisex": ["top", "bottom", "shoes"],
}

def generate_meta_for_items_clean():
    """Generate meta.json files for all categories in ITEMS_CLEAN."""
    
    print("🔧 Generating meta.json files for ITEMS_CLEAN directory...\n")
    total_items = 0
    
    for gender in CATEGORIES.keys():
        for category in CATEGORIES[gender]:
            # Source: ITEMS_CLEAN directory
            clean_dir = ITEMS_CLEAN_ROOT / gender / category
            
            if not clean_dir.exists():
                print(f"⚠️  Skipping {gender}/{category} - directory not found")
                continue
            
            # Check embedding count
            emb_file = ITEM_EMB_ROOT / gender / category / "emb_30d.npy"
            if not emb_file.exists():
                print(f"⚠️  Skipping {gender}/{category} - no embeddings found")
                continue
            
            emb = np.load(emb_file)
            max_items = emb.shape[0]
            
            # Get all image files
            image_files = sorted(clean_dir.glob("*.jpg"))
            
            if not image_files:
                print(f"⚠️  No images found in {gender}/{category}")
                continue
            
            # Limit to number of embeddings
            if len(image_files) > max_items:
                print(f"⚠️  {gender}/{category}: Found {len(image_files)} images but only {max_items} embeddings - limiting to {max_items}")
                image_files = image_files[:max_items]
            elif len(image_files) < max_items:
                print(f"⚠️  {gender}/{category}: Found {len(image_files)} images but have {max_items} embeddings - using {len(image_files)}")
            
            # Generate metadata entries
            meta_list = []
            for img_path in image_files:
                item_id = img_path.stem  # e.g., "male_top_0001"
                
                meta_entry = {
                    "item_id": item_id,
                    "image_path": str(img_path.absolute()),
                    "gender": gender,
                    "category": category
                }
                meta_list.append(meta_entry)
            
            # Write meta.json to ITEM_EMB directory (where the embeddings are)
            emb_dir = ITEM_EMB_ROOT / gender / category
            emb_dir.mkdir(parents=True, exist_ok=True)
            
            meta_file = emb_dir / "meta.json"
            
            # Backup old meta.json if exists
            if meta_file.exists():
                backup_file = emb_dir / "meta.json.backup_official"
                if not backup_file.exists():
                    import shutil
                    shutil.copy2(meta_file, backup_file)
                    print(f"   📦 Backed up old meta.json to {backup_file.name}")
            
            # Write new meta.json
            with open(meta_file, 'w') as f:
                json.dump(meta_list, f, indent=2)
            
            status = "✅" if len(meta_list) == max_items else "⚠️"
            print(f"{status} {gender}/{category}: {len(meta_list)} items (emb={max_items}) → {meta_file.relative_to(ITEM_EMB_ROOT.parent)}")
            total_items += len(meta_list)
    
    print(f"\n{'='*60}")
    print(f"✅ DONE! Generated metadata for {total_items} items")
    print(f"{'='*60}")

if __name__ == "__main__":
    generate_meta_for_items_clean()
