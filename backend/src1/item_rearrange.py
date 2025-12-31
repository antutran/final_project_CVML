import os
import shutil
from pathlib import Path

# ===== CONFIG =====
SRC_ROOT = r"/Users/tuantran/Downloads/CVML/dataset/ITEM_OFFICIAL"        # folder hiện tại
DST_ROOT = r"/Users/tuantran/Downloads/CVML/dataset/ITEMS_CLEAN"  # folder mới sau khi clean

GENDER_MAP = {
    "Female": "female",
    "Male": "male",
    "Unisex": "unisex",
}

# category hợp lệ theo gender
CATEGORIES = {
    "female": ["top", "bottom", "shoes", "dress"],
    "male": ["top", "bottom", "shoes"],
    "unisex": ["top", "bottom", "shoes"],
}

IMG_EXTS = {".jpg", ".jpeg", ".png", ".webp"}


# ===== UTILS =====
def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


# ===== MAIN =====
def clean_items():
    counters = {}

    for src_gender_folder, gender in GENDER_MAP.items():
        src_gender_path = Path(SRC_ROOT) / src_gender_folder
        if not src_gender_path.exists():
            continue

        for category in CATEGORIES[gender]:
            counters[(gender, category)] = 1

            dst_cat_dir = Path(DST_ROOT) / gender / category
            ensure_dir(dst_cat_dir)

            src_cat_dir = src_gender_path / category
            if not src_cat_dir.exists():
                continue

            # walk toàn bộ subfolder style (elegant, casual, street, ...)
            for root, _, files in os.walk(src_cat_dir):
                for fname in files:
                    ext = Path(fname).suffix.lower()
                    if ext not in IMG_EXTS:
                        continue

                    src_img = Path(root) / fname

                    idx = counters[(gender, category)]
                    new_name = f"{gender}_{category}_{idx:04d}{ext}"
                    dst_img = dst_cat_dir / new_name

                    shutil.copy2(src_img, dst_img)
                    counters[(gender, category)] += 1

    print("✅ DONE. Items cleaned & renamed successfully.")


if __name__ == "__main__":
    clean_items()
