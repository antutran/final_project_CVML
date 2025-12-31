import clip
import torch
import numpy as np
import json
from PIL import Image
from pathlib import Path
from tqdm import tqdm

# ================= CONFIG =================
ITEM_IMG_ROOT = Path("D:/CVML/ITEMS_CLEAN")
OUT_ROOT = Path("D:/CVML/ITEM_EMB")

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# ================= LOAD CLIP =================
print("Using device:", DEVICE)
model, preprocess = clip.load("ViT-B/32", device=DEVICE)
model.eval()

# ================= EMBED ONE FOLDER =================
def embed_item_folder(img_dir: Path, out_dir: Path):
    img_paths = sorted([p for p in img_dir.iterdir() if p.suffix.lower() in IMAGE_EXTS])
    if len(img_paths) == 0:
        return

    embeddings = []
    meta = []

    with torch.no_grad():
        for p in tqdm(img_paths, desc=f"Embedding {img_dir}"):
            img = Image.open(p).convert("RGB")
            img = preprocess(img).unsqueeze(0).to(DEVICE)

            emb = model.encode_image(img)
            emb = emb / emb.norm(dim=-1, keepdim=True)

            embeddings.append(emb.cpu().numpy()[0])

            meta.append({
                "item_id": p.stem,               # female_top_0001
                "image_path": str(p),            # path đầy đủ
                "gender": img_dir.parent.name,   # female / male / unisex
                "category": img_dir.name         # top / bottom / shoes / dress
            })

    out_dir.mkdir(parents=True, exist_ok=True)
    np.save(out_dir / "emb.npy", np.vstack(embeddings))
    with open(out_dir / "meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    print(f"✅ Saved {out_dir} ({len(embeddings)} items)")


# ================= MAIN =================
for gender_dir in ITEM_IMG_ROOT.iterdir():
    if not gender_dir.is_dir():
        continue

    for category_dir in gender_dir.iterdir():
        if not category_dir.is_dir():
            continue

        out_dir = OUT_ROOT / gender_dir.name / category_dir.name
        embed_item_folder(category_dir, out_dir)

print("\n🎉 ITEM EMBEDDING DONE.")
