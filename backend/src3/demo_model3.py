import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from src2.model2 import model2_recommend
from src2.kol_condition import condition_kol
from src3.model3 import model3_recommend
from src3.visualize_outfits import show_outfit

# =========================
# CONFIG
# =========================
BASE_DIR = Path("D:/CVML")

USER_STYLE_PATH = BASE_DIR / "styles" / "User" / "userm3_style.npy"
KOL_CLUSTER_PATH = BASE_DIR / "styles" / "KOL" / "KOL_streetwear_Natalie_Alysa_clusters.npy"

GENDER = "male"
BETA = 0.5
ALPHAS = [0.1, 0.3, 0.5, 0.7, 0.9]


# =========================
# LOAD
# =========================
print("🔄 Loading user style...")
user_vec = np.load(USER_STYLE_PATH)

print("🔄 Loading KOL clusters...")
kol_clusters = np.load(KOL_CLUSTER_PATH)

# =========================
# MODEL 2
# =========================
print("🚀 Running Model 2...")
picked = model2_recommend(
    user_vec=user_vec,
    kol_clusters=kol_clusters,
    gender=GENDER,
    beta=BETA
)

# =========================
# CONDITION KOL (ONCE)
# =========================
kol_vec, _, _ = condition_kol(user_vec, kol_clusters)

# =========================
# MODEL 3
# =========================
print("🧠 Running Model 3...")
result = model3_recommend(
    user_vec=user_vec,
    kol_vec=kol_vec,
    cand=picked["items"] if "items" in picked else picked,
    gender=GENDER,
    alphas=ALPHAS
)

print("\n✅ Best alpha:", result["alpha_best"])
print("📊 Alpha scores:", result["alpha_scores"])

for i, o in enumerate(result["outfits"], 1):
    print(f"\n--- Outfit {i} ---")
    print(f"score={o['score']:.4f}, style_fit={o['style_fit']:.4f}, coh={o['coherence']:.4f}")
    for r, m in zip(o["roles"], o["items"]):
        name = m.get("name") or m.get("filename") or m.get("path") or m.get("image_path")
        print(f"  {r}: {name}")



for i, o in enumerate(result["outfits"], 1):
    show_outfit(o, title=f"Outfit #{i} | alpha={result['alpha_best']}")
