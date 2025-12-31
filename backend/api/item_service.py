import json
import os
from pathlib import Path
from typing import Dict, Optional, Any

class ItemService:
    """Service for managing item metadata and image lookups."""
    
    def __init__(self, item_emb_root: Path):
        self.root = item_emb_root
        self.item_cache: Dict[str, str] = {}  # item_id -> image_path
        self._load_all_metadata()
        
    def _load_all_metadata(self):
        """Build a cache of all item_ids to their image paths."""
        if not self.root.exists():
            print(f"⚠️  Warning: Item root not found: {self.root}")
            return

        print(f"🔍 Loading item metadata from {self.root}...")
        count = 0
        # Iterate through gender/category/meta.json
        for gender_dir in self.root.iterdir():
            if not gender_dir.is_dir():
                continue
                
            for category_dir in gender_dir.iterdir():
                if not category_dir.is_dir():
                    continue
                    
                meta_file = category_dir / "meta.json"
                if meta_file.exists():
                    try:
                        with open(meta_file, "r") as f:
                            meta_list = json.load(f)
                            for item in meta_list:
                                item_id = item.get("item_id")
                                image_path = item.get("image_path")
                                if item_id and image_path:
                                    # Translate host path to container path
                                    if image_path.startswith("/Users/tuantran/Downloads/CVML/dataset"):
                                        image_path = image_path.replace("/Users/tuantran/Downloads/CVML/dataset", "/app/dataset")
                                    
                                    self.item_cache[item_id] = image_path
                                    count += 1
                    except Exception as e:
                        print(f"Error loading {meta_file}: {e}")
        
        print(f"✅ Loaded {count} items into cache")

    def get_image_path(self, item_id: str) -> Optional[str]:
        """Get the absolute image path for an item ID."""
        return self.item_cache.get(item_id)
