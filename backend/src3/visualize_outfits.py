import matplotlib.pyplot as plt
from PIL import Image
from matplotlib.widgets import CheckButtons
from pathlib import Path


def show_outfits_with_selection(outfits, title=None):
    """
    Display outfits and allow user to select preferred ones.
    Returns: list of selected outfit indices.
    """
    n_outfits = len(outfits)
    n_items = max(len(o["items"]) for o in outfits)

    fig, axes = plt.subplots(
        n_items,
        n_outfits,
        figsize=(3 * n_outfits, 3 * n_items)
    )

    if n_items == 1:
        axes = [axes]

    for col, outfit in enumerate(outfits):
        items = outfit["items"]
        roles = outfit["roles"]

        for row in range(n_items):
            ax = axes[row][col]
            ax.axis("off")

            if row >= len(items):
                continue

            meta = items[row]
            role = roles[row]

            path = (
                meta.get("image_path")
                or meta.get("path")
                or meta.get("filename")
            )

            try:
                img = Image.open(path).convert("RGB")
                ax.imshow(img)
            except (FileNotFoundError, OSError):
                # Create a placeholder image if file not found
                placeholder = Image.new('RGB', (224, 224), color=(200, 200, 200))
                ax.imshow(placeholder)
                ax.text(112, 112, f"Image\nNot Found\n{Path(path).name}", 
                       ha='center', va='center', fontsize=10, color='red')

            if col == 0:
                ax.set_ylabel(role, fontsize=12)

            if row == 0:
                ax.set_title(f"Outfit {col+1}", fontsize=13)

    if title:
        fig.suptitle(title, fontsize=15)

    # ---- Checkboxes
    rax = plt.axes([0.02, 0.25, 0.15, 0.5])
    labels = [f"O{i+1}" for i in range(n_outfits)]
    visibility = [False] * n_outfits

    check = CheckButtons(rax, labels, visibility)
    selected = set()

    def on_click(label):
        idx = labels.index(label)
        if idx in selected:
            selected.remove(idx)
        else:
            selected.add(idx)

    check.on_clicked(on_click)

    plt.tight_layout(rect=[0.18, 0.05, 1, 0.95])
    plt.show()

    return sorted(selected)
