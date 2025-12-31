import numpy as np
from pathlib import Path
from model2 import model2_recommend
from visualize_items_with_ruler import visualize_items_with_ruler


# =========================================================
# CONFIG
# =========================================================
BASE_DIR = Path("D:/CVML")

USER_STYLE_PATH = BASE_DIR / "styles" / "User" / "userm2_style.npy"
KOL_CLUSTER_PATH = BASE_DIR / "styles" / "KOL" / "KOL_sportwear_Neymar_clusters.npy"

GENDER = "male"   # "male" | "female"


# =========================================================
# LOAD DATA
# =========================================================
print("🔄 Loading user style...")
user_vec = np.load(USER_STYLE_PATH)
print("User vec shape:", user_vec.shape)

print("🔄 Loading KOL clusters...")
kol_clusters = np.load(KOL_CLUSTER_PATH)
print("KOL clusters shape:", kol_clusters.shape)


# =========================================================
# RUN MODEL 2
# =========================================================
print("🚀 Running Model 2 recommendation...")
picked = model2_recommend(
    user_vec=user_vec,
    kol_clusters=kol_clusters,
    gender=GENDER,
    beta=0.8
)




visualize_items_with_ruler(picked)
