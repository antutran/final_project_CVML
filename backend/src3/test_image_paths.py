import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from src2.item_repository import load_pool
import json

# Test loading male top items
emb, meta = load_pool("male", "top")

print(f"Loaded {len(meta)} items")
print("\nFirst 3 items:")
for i, item in enumerate(meta[:3]):
    print(f"\n{i+1}. {item['item_id']}")  
    print(f"   Path: {item['image_path']}")
    # Check if file exists
    from pathlib import Path
    exists = Path(item['image_path']).exists()
    print(f"   Exists: {exists}")
