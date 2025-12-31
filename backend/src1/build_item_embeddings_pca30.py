import numpy as np
import joblib
from pathlib import Path

# =========================================================
# CONFIG
# =========================================================
ITEM_EMB_ROOT = Path("ITEM_EMB")     # nơi chứa emb.npy
PCA_PATH = Path("models/pca_30d.joblib")

# =========================================================
# LOAD PCA
# =========================================================
print("🔄 Loading PCA model...")
pca = joblib.load(PCA_PATH)

# =========================================================
# UTILS
# =========================================================
def l2norm(x: np.ndarray) -> np.ndarray:
    return x / (np.linalg.norm(x, axis=1, keepdims=True) + 1e-12)

# =========================================================
# PROCESS ALL ITEM FOLDERS
# =========================================================
count = 0

for gender_dir in ITEM_EMB_ROOT.iterdir():
    if not gender_dir.is_dir():
        continue

    for cat_dir in gender_dir.iterdir():
        if not cat_dir.is_dir():
            continue

        emb_path = cat_dir / "emb.npy"
        if not emb_path.exists():
            continue

        print(f"\n📂 Processing {emb_path}")

        # load 512D embeddings
        X = np.load(emb_path)                  # (N, 512)
        assert X.ndim == 2, f"Invalid shape: {X.shape}"

        # normalize 512D
        X = l2norm(X)

        # PCA → 30D
        X30 = pca.transform(X)                 # (N, 30)
        X30 = l2norm(X30)

        # save
        out_path = cat_dir / "emb_30d.npy"
        np.save(out_path, X30.astype("float32"))

        print(f"✅ Saved {out_path} {X30.shape}")
        count += 1

print(f"\n🎉 DONE. Converted {count} item folders to PCA 30D.")
