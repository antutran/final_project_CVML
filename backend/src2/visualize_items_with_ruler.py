from PIL import Image
import matplotlib.pyplot as plt
from pathlib import Path

def visualize_items_with_ruler(result):
    items = result["items"]
    roles = list(items.keys())

    max_len = max(len(v) for v in items.values())

    fig, axes = plt.subplots(
        nrows=len(roles),
        ncols=max_len,
        figsize=(3 * max_len, 3 * len(roles))
    )

    if len(roles) == 1:
        axes = [axes]

    for r, role in enumerate(roles):
        for c in range(max_len):
            ax = axes[r][c]
            ax.axis("off")

            if c >= len(items[role]):
                continue

            meta = items[role][c][0]
            img = Image.open(Path(meta["image_path"])).convert("RGB")

            ax.imshow(img)
            if c == 0:
                ax.set_ylabel(role.upper(), fontsize=14)

    # draw ruler
    fig.suptitle("Model 2 – Picked Items (Style Intersection)", fontsize=16)
    plt.tight_layout()
    plt.show()
