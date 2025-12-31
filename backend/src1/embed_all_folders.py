import clip
import torch
import numpy as np
from PIL import Image
from pathlib import Path
from tqdm import tqdm

# ---------------- CONFIG ----------------
DATA_DIR = Path("data")
OUT_DIR = Path("embeddings")
IMAGE_EXTS = [".jpg", ".png", ".jpeg"]

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# ---------------- LOAD CLIP ----------------
print("Using device:", DEVICE)
model, preprocess = clip.load("ViT-B/32", device=DEVICE)
model.eval()

# ---------------- EMBED FUNCTION ----------------
def embed_folder(img_dir: Path):
    img_paths = sorted(
        [p for p in img_dir.iterdir() if p.suffix.lower() in IMAGE_EXTS]
    )

    assert len(img_paths) > 0, f"No images in {img_dir}"

    embeddings = []

    with torch.no_grad():
        for p in tqdm(img_paths, desc=f"Embedding {img_dir.name}"):
            img = Image.open(p).convert("RGB")
            img = preprocess(img).unsqueeze(0).to(DEVICE)

            emb = model.encode_image(img)
            emb = emb / emb.norm(dim=-1, keepdim=True)

            embeddings.append(emb.cpu().numpy())

    return np.vstack(embeddings)  # (N, 512)

# ---------------- MAIN ----------------
for category in ["KOL", "User"]:
    in_root = DATA_DIR / category
    out_root = OUT_DIR / category
    out_root.mkdir(parents=True, exist_ok=True)

    for folder in in_root.iterdir():
        if not folder.is_dir():
            continue

        print(f"\n📂 Processing {category}/{folder.name}")
        emb = embed_folder(folder)

        out_path = out_root / f"{folder.name}.npy"
        np.save(out_path, emb)

        print(f"✅ Saved: {out_path} {emb.shape}")

print("\n🎉 All embeddings completed.")
