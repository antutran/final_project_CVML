import numpy as np
from pathlib import Path
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import joblib

# ================= CONFIG =================
EMB_DIR = Path("embeddings/KOL")
PCA_PATH = Path("models/pca_30d.joblib")

K_RANGE = range(2, 7)
RANDOM_STATE = 42
MIN_SAMPLES = 10   # bỏ KOL quá ít ảnh

# ================= LOAD PCA =================
pca = joblib.load(PCA_PATH)

print("\n📊 Checking KMeans per KOL\n")

for emb_path in EMB_DIR.glob("*.npy"):
    kol_id = emb_path.stem
    E = np.load(emb_path)

    if E.shape[0] < MIN_SAMPLES:
        print(f"⚠️ {kol_id}: skipped (only {E.shape[0]} samples)")
        continue

    # normalize + PCA
    E = E / np.linalg.norm(E, axis=1, keepdims=True)
    X = pca.transform(E)

    print(f"\n👤 KOL: {kol_id} ({X.shape[0]} samples)")
    print(f"{'K':>3} | {'Silhouette':>10}")
    print("-" * 18)

    best_k = None
    best_sil = -1

    for k in K_RANGE:
        if k >= X.shape[0]:
            continue

        kmeans = KMeans(
            n_clusters=k,
            n_init=10,
            random_state=RANDOM_STATE
        )
        labels = kmeans.fit_predict(X)

        sil = silhouette_score(X, labels)
        print(f"{k:>3} | {sil:10.4f}")

        if sil > best_sil:
            best_sil = sil
            best_k = k

    print(f"✅ Best K for {kol_id}: {best_k} (sil={best_sil:.4f})")
