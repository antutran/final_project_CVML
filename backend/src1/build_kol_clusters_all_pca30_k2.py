import numpy as np
from pathlib import Path
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import joblib

# =========================================================
# CONFIG
# =========================================================
EMB_DIR = Path("embeddings/KOL")
OUT_DIR = Path("styles/KOL")
MODEL_DIR = Path("models")

PCA_DIM = 30
K = 2
RANDOM_STATE = 42

OUT_DIR.mkdir(parents=True, exist_ok=True)
MODEL_DIR.mkdir(parents=True, exist_ok=True)

# =========================================================
# LOAD ALL KOL EMBEDDINGS (FOR GLOBAL PCA)
# =========================================================
all_embeddings = []
kol_embeddings = {}

for emb_path in EMB_DIR.glob("*.npy"):
    E = np.load(emb_path)              # (N, 512)
    E = E / np.linalg.norm(E, axis=1, keepdims=True)

    kol_embeddings[emb_path.stem] = E
    all_embeddings.append(E)

assert len(all_embeddings) > 0, "❌ No KOL embeddings found!"

all_embeddings = np.vstack(all_embeddings)

print(f"📊 Fitting PCA on {all_embeddings.shape[0]} samples")

# =========================================================
# FIT PCA (GLOBAL)
# =========================================================
pca = PCA(n_components=PCA_DIM, random_state=RANDOM_STATE)
pca.fit(all_embeddings)

explained_var = pca.explained_variance_ratio_.sum()
print(f"✅ PCA explained variance: {explained_var:.3f}")

# save PCA model
pca_path = MODEL_DIR / "pca_30d.joblib"
joblib.dump(pca, pca_path)
print(f"💾 Saved PCA model → {pca_path}")

# =========================================================
# BUILD CLUSTERS FOR EACH KOL
# =========================================================
for kol_id, E in kol_embeddings.items():
    print("\n" + "=" * 70)
    print(f"📂 Processing KOL: {kol_id}")

    # PCA transform
    X = pca.transform(E)        # (N, 30)

    # KMeans
    kmeans = KMeans(
        n_clusters=K,
        n_init=10,
        random_state=RANDOM_STATE
    )
    labels = kmeans.fit_predict(X)

    # Silhouette (sanity check)
    sil = silhouette_score(X, labels)
    print(f"Silhouette (K=2): {sil:.3f}")

    # ===== BUILD NUMERIC CLUSTER CENTROIDS =====
    centroids = []

    for cid in range(K):
        members = X[labels == cid]
        centroid = members.mean(axis=0)
        centroid /= np.linalg.norm(centroid)
        centroids.append(centroid)

        print(f"  - Cluster {cid}: {len(members)} samples")

    # (K, 30) float32 — CHUẨN MODEL 2
    centroids = np.stack(centroids, axis=0).astype("float32")

    out_path = OUT_DIR / f"{kol_id}_clusters.npy"
    np.save(out_path, centroids)

    print(f"💾 Saved → {out_path} {centroids.shape}")

print("\n🎉 All KOL clusters built (PCA 30D + KMeans K=2).")
