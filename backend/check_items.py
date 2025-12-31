
import sys
from pathlib import Path

# Add backend to path
sys.path.append("/Users/tuantran/Downloads/CVML/backend")

from api.item_service import ItemService
from src2.config import ITEM_EMB_ROOT

print(f"ITEM_EMB_ROOT: {ITEM_EMB_ROOT}")
item_service = ItemService(item_emb_root=ITEM_EMB_ROOT)

print(f"Total items in cache: {len(item_service.item_cache)}")

if len(item_service.item_cache) > 0:
    first_key = list(item_service.item_cache.keys())[0]
    first_path = item_service.item_cache[first_key]
    print(f"Sample item: {first_key} -> {first_path}")
    print(f"Path exists: {Path(first_path).exists()}")
else:
    print("Cache is empty!")
