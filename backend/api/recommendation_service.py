"""
Recommendation service wrapping the existing recommendation pipeline.

Adapts the logic from src3/demo_alpha_online.py into a request-driven architecture
while preserving all existing model logic.
"""

import numpy as np
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add parent directory to path for imports
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


# Constants from demo_alpha_online.py
POOL_PER_ROLE = 35
NUM_SAMPLES = 160
TEMP = 0.22
FINAL_K = 8
MAX_USE_PER_ITEM = 1
LAMBDA_DIV = 0.55
LAMBDA_COH = 0.30
EPS_BETA = 0.15


class RecommendationService:
    """
    Service for generating outfit recommendations and processing feedback.
    
    Preserves the exact logic from demo_alpha_online.py but in a stateless,
    request-driven architecture.
    """
    
    @staticmethod
    def generate_outfits(
        user_vec: np.ndarray,
        kol_clusters: np.ndarray,
        gender: str,
        state: Dict[str, Any],
        anti_repeat: AntiRepeatMemory,
        auto_learn: bool = True,
        manual_alpha: Optional[float] = None,
        manual_beta: Optional[float] = None,
        diversity: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate outfit recommendations.
        
        Args:
            user_vec: 30D user style vector
            kol_clusters: KOL cluster embeddings
            gender: "male" or "female"
            state: Session state with alpha_grid, alpha_stats, beta, pref, conf
            anti_repeat: AntiRepeatMemory instance
            auto_learn: If True, use UCB for alpha and auto-update beta. If False, use manual values.
            manual_alpha: Manual alpha value (0-1), used when auto_learn=False
            manual_beta: Manual beta value (0-1), used when auto_learn=False
            diversity: If True, increase diversity in outfit generation
            
        Returns:
            Dict with:
                - outfits: List of recommended outfits
                - alpha: Alpha value used
                - beta: Beta value (before exploration)
                - beta_used: Beta value after exploration mix
                - pref: Current preference
                - conf: Current confidence
                - step: Current step number
        """
        # Increment step
        state["step"] = int(state.get("step", 0)) + 1
        
        # Extract state
        pref = float(state.get("pref", 0.0))
        conf = float(state.get("conf", 0.0))
        beta = float(state.get("beta", 0.5))
        
        # Determine alpha and beta based on mode
        if auto_learn:
            # Auto mode: Use UCB for alpha
            alpha_used = pick_alpha_ucb(
                alpha_grid=state["alpha_grid"],
                alpha_stats=state["alpha_stats"],
                pref=pref
            )
            state["alpha_current"] = alpha_used
            
            # Apply exploration mix to beta
            beta_used = exploration_mix(beta, eps=EPS_BETA)
        else:
            # Manual mode: Use provided values
            alpha_used = manual_alpha if manual_alpha is not None else 0.5
            beta_used = manual_beta if manual_beta is not None else 0.5
            state["alpha_current"] = alpha_used
            # In manual mode, we don't apply exploration mix to beta
        
        # Condition KOL
        kol_vec, _, _ = condition_kol(user_vec, kol_clusters)
        
        # Model 2: Pick candidate items
        picked = model2_recommend(
            user_vec=user_vec,
            kol_clusters=kol_clusters,
            gender=gender,
            beta=beta_used
        )
        
        # Adjust diversity parameters if requested
        lambda_div = 0.75 if diversity else LAMBDA_DIV  # Increase from 0.55 to 0.75 for more diversity
        
        # Model 3: Generate and score outfits
        result = model3_recommend(
            user_vec=user_vec,
            kol_vec=kol_vec,
            cand=picked["items"],
            gender=gender,
            alpha_current=alpha_used,
            pool_per_role=POOL_PER_ROLE,
            num_samples=NUM_SAMPLES,
            temperature=TEMP,
            lambda_coh=LAMBDA_COH,
            anti_repeat=anti_repeat,
            lambda_div=lambda_div,
            max_use_per_item=MAX_USE_PER_ITEM,
            final_k=FINAL_K,
        )
        
        # Format outfits for frontend (removes NumPy arrays)
        formatted_outfits = [
            RecommendationService.format_outfit_for_frontend(o, idx) 
            for idx, o in enumerate(result["outfits"])
        ]
        
        return {
            "outfits": formatted_outfits,
            "alpha": float(alpha_used),
            "beta": float(beta),
            "beta_used": float(beta_used),
            "pref": float(pref),
            "conf": float(conf),
            "step": int(state["step"]),
            "n_candidates": int(result.get("n_candidates", 0)),
        }
    
    @staticmethod
    def process_feedback(
        selected_indices: List[int],
        outfits: List[Dict[str, Any]],
        user_vec: np.ndarray,
        kol_clusters: np.ndarray,
        state: Dict[str, Any],
        anti_repeat: AntiRepeatMemory,
    ) -> Dict[str, Any]:
        """
        Process user feedback and update state.
        
        Args:
            selected_indices: Indices of selected outfits (0-based)
            outfits: List of outfits that were shown
            user_vec: User style vector
            kol_clusters: KOL cluster embeddings
            state: Session state
            anti_repeat: AntiRepeatMemory instance
            
        Returns:
            Updated state dict with new alpha_stats, pref, conf, beta
        """
        # Update anti-repeat memory with all shown outfits
        anti_repeat.update(outfits)
        
        # Calculate reward from feedback
        alpha_used = state.get("alpha_current", 0.5)
        r = reward_from_feedback(selected_indices, shown_n=len(outfits))
        
        # Update alpha stats
        state["alpha_stats"] = update_alpha_stats(
            state["alpha_stats"], 
            alpha_used, 
            r
        )
        
        # If no selection, just save state and return
        if not selected_indices:
            return {
                "updated": False,
                "reward": float(r),
                "pref": float(state.get("pref", 0.0)),
                "conf": float(state.get("conf", 0.0)),
                "beta": float(state.get("beta", 0.5)),
            }
        
        # Get selected outfits and reconstruct with embeddings
        # Frontend sends outfits without embeddings, we need to rebuild them
        from src2.item_repository import load_with_unisex
        
        selected_outfits_with_embs = []
        for idx in selected_indices:
            if idx >= len(outfits):
                continue
            outfit = outfits[idx]
            items = outfit.get("items", [])
            
            # Reconstruct embeddings from item_ids
            embs_list = []
            for item in items:
                item_id = item.get("id") or item.get("item_id", "")
                if not item_id:
                    continue
                    
                # Extract gender and category from item_id
                # Format: male_top_0001 or female_bottom_0002
                parts = item_id.split("_")
                if len(parts) >= 3:
                    gender = parts[0]  # male, female, unisex
                    category = parts[1]  # top, bottom, shoes, dress
                    
                    try:
                        # Load all items for this category
                        emb_pool, meta_pool = load_with_unisex(gender, category)
                        
                        # Find matching item by ID
                        for i, meta in enumerate(meta_pool):
                            if meta.get("item_id") == item_id:
                                embs_list.append(emb_pool[i])
                                break
                    except Exception as e:
                        print(f"Warning: Could not load embedding for {item_id}: {e}")
                        continue
            
            if embs_list:
                selected_outfits_with_embs.append({
                    "embs": np.array(embs_list)
                })
        
        if not selected_outfits_with_embs:
            # Could not reconstruct any outfits with embeddings
            return {
                "updated": False,
                "reward": float(r),
                "pref": float(state.get("pref", 0.0)),
                "conf": float(state.get("conf", 0.0)),
                "beta": float(state.get("beta", 0.5)),
            }
        
        # Condition KOL to get kol_vec
        kol_vec, _, _ = condition_kol(user_vec, kol_clusters)
        
        # Calculate preference direction using reconstructed outfits
        dir_value = direction_from_selected_outfits(
            selected_outfits_with_embs, user_vec, kol_vec
        )
        
        print(f"DEBUG: dir_value = {dir_value}")
        
        # Update pref and conf
        pref = float(state.get("pref", 0.0))
        conf = float(state.get("conf", 0.0))
        
        print(f"DEBUG: Before update - pref={pref}, conf={conf}, reward={r}")
        
        pref_new, conf_new, signal = update_pref_conf(
            pref=pref,
            conf=conf,
            dir_value=dir_value,
            reward=r
        )
        
        print(f"DEBUG: After update - pref_new={pref_new}, conf_new={conf_new}, signal={signal}")
        
        # Update beta from pref/conf
        beta = float(state.get("beta", 0.5))
        beta_new = update_beta_from_pref(
            beta=beta,
            pref=pref_new,
            conf=conf_new
        )
        
        # Apply entropy kick if needed
        recent = list(anti_repeat.item_memory)[-5:]
        if recent:
            flat = [k for items in recent for k in items]
            repeat_ratio = 1.0 - len(set(flat)) / max(1, len(flat))
        else:
            repeat_ratio = 0.0
        
        beta_new = beta_entropy_kick(beta_new, repeat_ratio)
        
        # Anti-stuck mechanism
        last_pref = float(state.get("last_pref", pref))
        last_beta = float(state.get("last_beta", beta))
        stuck_steps = int(state.get("stuck_steps", 0))
        
        dp = abs(pref_new - last_pref)
        db = abs(beta_new - last_beta)
        
        if dp < 0.015 and db < 0.02:
            stuck_steps += 1
        else:
            stuck_steps = 0
        
        if stuck_steps >= 6:
            beta_new = exploration_mix(beta_new, eps=0.35)
            stuck_steps = 0
        
        # Update state
        state["pref"] = pref_new
        state["conf"] = conf_new
        state["beta"] = beta_new
        state["last_pref"] = pref_new
        state["last_beta"] = beta_new
        state["stuck_steps"] = stuck_steps
        
        return {
            "updated": True,
            "reward": float(r),
            "dir_value": float(dir_value),
            "signal": float(signal),
            "pref": float(pref_new),
            "pref_change": float(pref_new - pref),
            "conf": float(conf_new),
            "beta": float(beta_new),
            "beta_change": float(beta_new - beta),
            "repeat_ratio": float(repeat_ratio),
            "stuck_steps": stuck_steps,
        }
    
    @staticmethod
    def format_outfit_for_frontend(outfit: Dict[str, Any], index: int = 0) -> Dict[str, Any]:
        """
        Format outfit data for frontend consumption.
        
        Args:
            outfit: Outfit dict from model3
            index: Index of outfit in the list (for unique ID generation)
            
        Returns:
            Frontend-friendly outfit dict
        """
        import time
        
        # Extract items and roles
        items_list = outfit.get("items", [])
        roles_list = outfit.get("roles", [])
        
        # Generate unique outfit ID based on items
        item_ids = []
        for item in items_list:
            item_id = (
                item.get("item_id") or 
                item.get("id") or 
                item.get("filename") or
                ""
            )
            if not item_id and "image_path" in item:
                from pathlib import Path
                item_id = Path(item["image_path"]).stem
            if item_id:
                item_ids.append(item_id)
        
        # Create unique ID from combination of item IDs and timestamp
        outfit_id = f"outfit_{index}_{int(time.time() * 1000) % 100000}_{'_'.join(item_ids[:2])}"
        
        formatted = {
            "id": outfit_id,  # Add unique ID for frontend
            "items": [],
            "score": float(outfit.get("score", 0.0)),
            "style_fit": float(outfit.get("style_fit", 0.0)),
            "coherence": float(outfit.get("coherence", 0.0)),
            "alpha_used": float(outfit.get("alpha_used", 0.5)),
        }
        
        # Format each item with its corresponding role
        for idx, item in enumerate(items_list):
            # Try multiple field names to get item_id
            item_id = (
                item.get("item_id") or 
                item.get("id") or 
                item.get("filename") or
                ""
            )
            
            # If still no item_id, try to extract from image_path
            if not item_id and "image_path" in item:
                from pathlib import Path
                # Extract filename without extension as item_id
                item_id = Path(item["image_path"]).stem
            
            # Get role from roles_list if available
            role = roles_list[idx] if idx < len(roles_list) else item.get("role", "unknown")
            
            formatted["items"].append({
                "role": role,
                "image_url": f"/api/item/{item_id}/image" if item_id else "",
                "id": item_id,
            })
        
        return formatted
