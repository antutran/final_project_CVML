from pathlib import Path

# =========================================================
# PROJECT ROOT
# =========================================================
# Dynamic path resolution - points to backend directory root
BASE_DIR = Path(__file__).resolve().parents[1]

# =========================================================
# PATHS – DATA & EMBEDDINGS
# =========================================================
ITEM_EMB_ROOT = BASE_DIR / "ITEM_EMB"
USER_STYLE_ROOT = BASE_DIR / "styles" / "User"
KOL_STYLE_ROOT  = BASE_DIR / "styles" / "KOL"

# =========================================================
# MODEL 2 – ITEM PICKING CONFIG
# =========================================================

# Number of items picked per role
TOPK_PICK = 5

# Default style prior (β)
# β controls whether picked items are closer to USER or KOL
DEFAULT_BETA = 0.6

# Roles per gender
ROLES_BY_GENDER = {
    "male":   ["top", "bottom", "shoes"],
    "female": ["top", "bottom", "shoes", "dress"],
}

# =========================================================
# MODEL 3 – OUTFIT REASONING CONFIG
# =========================================================

# Candidate alphas to search (style trade-off)
ALPHA_CANDIDATES = [0.1, 0.3, 0.5, 0.7, 0.9]

# Outfit scoring weights
LAMBDA_STYLE   = 1.0   # style_fit weight
LAMBDA_QUALITY = 0.6   # outfit quality (coherence, color, pattern)

# Coherence weight inside outfit quality
LAMBDA_COHERENCE = 0.3

# =========================================================
# OUTFIT GENERATION
# =========================================================

# Limit items per role when generating outfits
TOPK_PER_ROLE_FOR_OUTFIT = 3

# Max number of outfits kept after scoring
MAX_OUTFITS_RETURNED = 5

# =========================================================
# DEBUG / VISUALIZATION
# =========================================================
DEBUG = True
