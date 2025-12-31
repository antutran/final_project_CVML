# src3/alpha_state.py
import json
from pathlib import Path


def default_state(alpha_grid=None):
    alpha_grid = alpha_grid or [0.1, 0.3, 0.5, 0.7, 0.9]
    return {
        "alpha_grid": [float(a) for a in alpha_grid],
        "alpha_stats": {str(float(a)): {"trials": 0, "reward_sum": 0.0} for a in alpha_grid},
        "alpha_current": 0.5,
        "beta": 0.5,
        "pref": 0.0,   # [-1,1] (kol=-1, user=+1)
        "conf": 0.0,   # [0,1]
        "step": 0,
    }


def load_state(path: Path, alpha_grid=None):
    if not path.exists():
        return default_state(alpha_grid)

    with open(path, "r") as f:
        st = json.load(f)

    # basic migration / fill missing keys
    base = default_state(alpha_grid or st.get("alpha_grid"))
    base.update(st)

    # ensure alpha_stats exist for all grid values
    grid = base["alpha_grid"]
    if "alpha_stats" not in base or not isinstance(base["alpha_stats"], dict):
        base["alpha_stats"] = {str(float(a)): {"trials": 0, "reward_sum": 0.0} for a in grid}
    else:
        for a in grid:
            k = str(float(a))
            if k not in base["alpha_stats"]:
                base["alpha_stats"][k] = {"trials": 0, "reward_sum": 0.0}

    return base


def save_state(path: Path, state: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(state, f, indent=2)
