import numpy as np
from pathlib import Path
import joblib

# =========================================================
# CONFIG
# =========================================================
EMB_DIR = Path("embeddings/User")
OUT_DIR = Path("styles/User")
PCA_PATH = Path("models/pca_30d.joblib")

OUT_DIR.mkdir(parents=True, exist_ok=True)

# =========================================================
# LOAD PCA
# =========================================================
pca = joblib.load(PCA_PATH)

# =========================================================
# PROCESS EACH USER
# =========================================================
for emb_path in EMB_DIR.glob("*.npy"):
    user_id = emb_path.stem

    E = np.load(emb_path)  # (N, 512)
    E = E / np.linalg.norm(E, axis=1, keepdims=True)

    # centroid in 512D
    centroid_512 = E.mean(axis=0)
    centroid_512 /= np.linalg.norm(centroid_512)

    # ---- PCA → 30D ----
    centroid_30 = pca.transform(centroid_512.reshape(1, -1))[0]
    centroid_30 /= np.linalg.norm(centroid_30)

    out_path = OUT_DIR / f"{user_id}_style.npy"
    np.save(out_path, centroid_30.astype("float32"))

    print(f"✅ Built USER style (30D) for {user_id}: {centroid_30.shape}")

print("\n🎉 All user styles built in PCA 30D.")
