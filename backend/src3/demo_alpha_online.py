import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from src2.kol_condition import condition_kol
from src2.model2 import model2_recommend

from src3.model3 import model3_recommend
from src3.anti_repeat import AntiRepeatMemory
from src3.alpha_online import (
    pick_alpha_ucb,
    update_alpha_stats,
    reward_from_feedback,
    direction_from_selected_outfits,
    update_pref_conf,
    update_beta_from_pref,
    exploration_mix,
    beta_entropy_kick,
)
from src3.alpha_state import load_state, save_state
from src3.visualize_outfits import show_outfits_with_selection

BASE_DIR = Path("/Users/tuantran/Downloads/CVML")
USER_STYLE_PATH = BASE_DIR / "backend/styles/User/userf1_style.npy"
KOL_CLUSTER_PATH = BASE_DIR / "backend/styles/KOL/KOL_formal_Andreas_Weinas_clusters.npy"

STATE_PATH = BASE_DIR / "backend/runs/online_state.json"
GENDER = "male"

ALPHA_GRID = [0.1, 0.3, 0.5, 0.7, 0.9]

POOL_PER_ROLE = 35
NUM_SAMPLES = 160
TEMP = 0.22

FINAL_K = 8
MAX_USE_PER_ITEM = 1
LAMBDA_DIV = 0.55
LAMBDA_COH = 0.30

EPS_BETA = 0.15


def main():
    print("🔄 Loading user & KOL...")
    user_vec = np.load(USER_STYLE_PATH)
    kol_clusters = np.load(KOL_CLUSTER_PATH)
    kol_vec, _, _ = condition_kol(user_vec, kol_clusters)

    st = load_state(STATE_PATH, alpha_grid=ALPHA_GRID)
    st.setdefault("stuck_steps", 0)
    st.setdefault("last_pref", st.get("pref", 0.0))
    st.setdefault("last_beta", st.get("beta", 0.5))

    anti_repeat = AntiRepeatMemory(maxlen=30, tau=8.0)

    while True:
        st["step"] = int(st.get("step", 0)) + 1

        pref = float(st.get("pref", 0.0))
        conf = float(st.get("conf", 0.0))
        beta = float(st.get("beta", 0.5))

        alpha_used = pick_alpha_ucb(
            alpha_grid=st["alpha_grid"],
            alpha_stats=st["alpha_stats"],
            pref=pref
        )
        st["alpha_current"] = alpha_used

        beta_used = exploration_mix(beta, eps=EPS_BETA)

        print(
            f"\n🎯 step={st['step']} | alpha={alpha_used:.2f} | "
            f"beta={beta:.3f} beta_used={beta_used:.3f} | "
            f"pref={pref:+.3f} conf={conf:.3f}"
        )

        picked = model2_recommend(
            user_vec=user_vec,
            kol_clusters=kol_clusters,
            gender=GENDER,
            beta=beta_used
        )

        result = model3_recommend(
            user_vec=user_vec,
            kol_vec=kol_vec,
            cand=picked["items"],
            gender=GENDER,
            alpha_current=alpha_used,
            pool_per_role=POOL_PER_ROLE,
            num_samples=NUM_SAMPLES,
            temperature=TEMP,
            lambda_coh=LAMBDA_COH,
            anti_repeat=anti_repeat,
            lambda_div=LAMBDA_DIV,
            max_use_per_item=MAX_USE_PER_ITEM,
            final_k=FINAL_K,
        )

        outfits = result["outfits"]

        selected_idx = show_outfits_with_selection(
            outfits,
            title=(
                f"alpha={alpha_used:.2f} | beta={beta:.2f} "
                f"(used {beta_used:.2f}) | pref={pref:+.2f} conf={conf:.2f}"
            )
        )

        anti_repeat.update(outfits)

        r = reward_from_feedback(selected_idx, shown_n=len(outfits))
        st["alpha_stats"] = update_alpha_stats(st["alpha_stats"], alpha_used, r)

        if not selected_idx:
            save_state(STATE_PATH, st)
            continue

        selected_outfits = [outfits[i] for i in selected_idx]
        dir_value = direction_from_selected_outfits(
            selected_outfits, user_vec, kol_vec
        )

        pref_new, conf_new, signal = update_pref_conf(
            pref=pref,
            conf=conf,
            dir_value=dir_value,
            reward=r
        )

        beta_new = update_beta_from_pref(
            beta=beta,
            pref=pref_new,
            conf=conf_new
        )

        # entropy kick
        recent = list(anti_repeat.item_memory)[-5:]
        if recent:
            flat = [k for items in recent for k in items]
            repeat_ratio = 1.0 - len(set(flat)) / max(1, len(flat))
        else:
            repeat_ratio = 0.0

        beta_new = beta_entropy_kick(beta_new, repeat_ratio)

        # anti-stuck
        dp = abs(pref_new - st["last_pref"])
        db = abs(beta_new - st["last_beta"])

        if dp < 0.015 and db < 0.02:
            st["stuck_steps"] += 1
        else:
            st["stuck_steps"] = 0

        if st["stuck_steps"] >= 6:
            beta_new = exploration_mix(beta_new, eps=0.35)
            st["stuck_steps"] = 0

        print(
            f"🧭 dir={dir_value:+.3f} signal={signal:+.3f} | "
            f"pref {pref:+.3f}->{pref_new:+.3f} | "
            f"beta {beta:.3f}->{beta_new:.3f} | reward={r:.3f}"
        )

        st["pref"] = pref_new
        st["conf"] = conf_new
        st["beta"] = beta_new
        st["last_pref"] = pref_new
        st["last_beta"] = beta_new

        save_state(STATE_PATH, st)


if __name__ == "__main__":
    main()
