# src3/alpha_online.py
import numpy as np


def cosine(a, b):
    return float(np.dot(a, b) / ((np.linalg.norm(a) + 1e-9) * (np.linalg.norm(b) + 1e-9)))


def direction_from_selected_outfits(selected_outfits, user_vec, kol_vec):
    """
    dir_value = mean(sim_user - sim_kol) over selected outfits
      >0 => leaning user
      <0 => leaning kol
    """
    if not selected_outfits:
        return 0.0

    diffs = []
    for o in selected_outfits:
        mean_emb = o["embs"].mean(axis=0)
        diffs.append(cosine(mean_emb, user_vec) - cosine(mean_emb, kol_vec))

    return float(np.mean(diffs))


# -----------------------------
# Preference state (pref/conf)
# -----------------------------
def update_pref_conf(
    pref: float,
    conf: float,
    dir_value: float,
    reward: float,
    lr_pref: float = 0.20,
    drift: float = 0.04,
    gamma_conf: float = 0.25,
    scale: float = 0.10,
):
    """
    PATCHED:
    - add pref fatigue (pref cao -> signal yếu)
    - keep hard cap ±0.85
    """
    base_signal = float(np.tanh(dir_value / max(1e-6, scale)))
    reward = float(np.clip(reward, 0.0, 1.0))

    MAX_PREF = 0.85

    # -------- PREF FATIGUE --------
    # pref càng gần trần -> signal càng yếu (nhưng không triệt tiêu)
    fatigue = 1.0 - min(0.6, abs(pref) / MAX_PREF)

    signal = base_signal * reward * fatigue

    # mean-reversion + learning
    pref_new = (1.0 - drift) * pref + lr_pref * signal
    pref_new = float(np.clip(pref_new, -MAX_PREF, MAX_PREF))

    # confidence follows effective signal
    target_conf = abs(signal)
    conf_new = (1.0 - gamma_conf) * conf + gamma_conf * target_conf
    conf_new = float(np.clip(conf_new, 0.0, 1.0))

    return pref_new, conf_new, signal



# -----------------------------
# Beta update (from pref/conf)
# -----------------------------
def update_beta_from_pref(
    beta: float,
    pref: float,
    conf: float,
    beta_span: float = 0.40,     # beta_target = 0.5 + beta_span*pref
    max_step: float = 0.10,      # your requirement: 0.07-0.1 should be possible
    smooth: float = 0.35,        # inertia
    conf_gate: float = 0.35,     # below this, drift back to 0.5
    drift_to_mid: float = 0.05,  # mean-reversion when low confidence
    min_beta: float = 0.05,
    max_beta: float = 0.95,
):
    pref = float(np.clip(pref, -1.0, 1.0))
    conf = float(np.clip(conf, 0.0, 1.0))

    beta_target = 0.5 + beta_span * pref
    beta_target = float(np.clip(beta_target, min_beta, max_beta))

    # smooth move toward target
    beta_proposed = (1.0 - smooth) * beta + smooth * beta_target

    # if not confident -> drift toward 0.5
    if conf < conf_gate:
        beta_proposed = (1.0 - drift_to_mid) * beta_proposed + drift_to_mid * 0.5

    # step cap (allows 0.07-0.1 when needed)
    # ---- asymmetric response: faster when pref decreases
    step_cap = max_step

    # if pref is pulling beta BACK toward 0.5, allow faster move
    if (beta > 0.5 and pref < 0) or (beta < 0.5 and pref > 0):
        step_cap = max_step * 1.6   # 👈 cho beta "nhả" nhanh hơn

    delta = float(np.clip(beta_proposed - beta, -step_cap, step_cap))
    beta_new = float(np.clip(beta + delta, min_beta, max_beta))

    # ---- SOFT CEILING (comfort zone)
    BETA_SOFT_MAX = 0.82
    CONF_STRONG = 0.70

    if beta_new > BETA_SOFT_MAX and conf < CONF_STRONG:
        beta_new = 0.7 * beta_new + 0.3 * BETA_SOFT_MAX

    return float(beta_new)



def exploration_mix(beta: float, eps: float = 0.15):
    """
    Keep a neutral portion always, to preserve "đường quay lại".
    """
    return float((1.0 - eps) * beta + eps * 0.5)


# -----------------------------
# Alpha bandit (UCB) on grid
# -----------------------------
def pick_alpha_ucb(alpha_grid, alpha_stats, pref=0.0, c=1.2, pref_bias=0.08):
    """
    UCB over discrete alpha grid.
    alpha_stats[a] has {trials, reward_sum}

    pref bias:
      pref>0 (lean user) -> slightly favor higher alpha
      pref<0 -> slightly favor lower alpha
    """
    alpha_grid = [float(a) for a in alpha_grid]
    total_trials = sum(alpha_stats.get(str(float(a)), {}).get("trials", 0) for a in alpha_grid) + 1

    # explore untried first
    for a in alpha_grid:
        s = alpha_stats.get(str(float(a)), {"trials": 0, "reward_sum": 0.0})
        if s["trials"] == 0:
            return float(a)

    best_a, best_val = None, -1e18
    for a in alpha_grid:
        s = alpha_stats[str(float(a))]
        t = max(1, int(s["trials"]))
        mean = float(s["reward_sum"]) / float(t)
        ucb = mean + c * float(np.sqrt(np.log(total_trials) / t))

        # bias by pref (very small, to avoid alpha "đâm thẳng")
        ucb += pref_bias * float(pref) * (float(a) - 0.5)

        if ucb > best_val:
            best_val = ucb
            best_a = float(a)

    return float(best_a if best_a is not None else 0.5)


def update_alpha_stats(alpha_stats, alpha_used, reward):
    k = str(float(alpha_used))
    if k not in alpha_stats:
        alpha_stats[k] = {"trials": 0, "reward_sum": 0.0}
    alpha_stats[k]["trials"] = int(alpha_stats[k]["trials"]) + 1
    alpha_stats[k]["reward_sum"] = float(alpha_stats[k]["reward_sum"]) + float(reward)
    return alpha_stats


def reward_from_feedback(selected_idx, shown_n):
    """
    Simple stable reward:
      reward = selection_rate in [0,1]
    """
    if shown_n <= 0:
        return 0.0
    return float(np.clip(len(selected_idx) / float(shown_n), 0.0, 1.0))

def beta_entropy_kick(
    beta: float,
    repeat_ratio: float,
    strength: float = 0.25,
    max_kick: float = 0.12,
    min_beta: float = 0.05,
    max_beta: float = 0.95,
):
    """
    repeat_ratio ∈ [0,1]: item repetition level
    If items repeat a lot -> push beta away from current side
    """
    repeat_ratio = float(np.clip(repeat_ratio, 0.0, 1.0))
    if repeat_ratio <= 0.05:
        return beta

    kick = min(max_kick, strength * repeat_ratio)

    # push away from current extreme
    direction = -1.0 if beta > 0.5 else 1.0
    beta_new = beta + direction * kick

    return float(np.clip(beta_new, min_beta, max_beta))
