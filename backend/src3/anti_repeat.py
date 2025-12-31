# src3/anti_repeat.py
from collections import deque
import math


class AntiRepeatMemory:
    """
    Partial anti-repeat (recency-weighted):
      - Penalize exact outfit repeats very strongly (recent -> stronger).
      - Penalize partial overlap (2/3, 1/3) with recency decay.
      - Add item cooldown penalty (same item reappears too often across turns).

    Only affects ranking; NOT alpha/beta learning.
    """

    def __init__(
        self,
        maxlen=30,
        tau=8.0,
        # overlap base penalties (before recency)
        p3=0.45,  # exact outfit repeat
        p2=0.22,
        p1=0.10,
        # item cooldown
        w_item=0.08,
        # hard cap
        max_penalty=0.55,
    ):
        self.memory = deque(maxlen=maxlen)      # list[set(keys)]
        self.item_memory = deque(maxlen=maxlen) # list[list(keys)]
        self.tau = float(tau)
        self.p3 = float(p3)
        self.p2 = float(p2)
        self.p1 = float(p1)
        self.w_item = float(w_item)
        self.max_penalty = float(max_penalty)

    @staticmethod
    def _key(meta):
        for k in ("image_path", "path", "filename", "id"):
            if isinstance(meta, dict) and k in meta and meta[k]:
                return meta[k]
        return None

    def outfit_signature(self, outfit):
        keys = []
        for item in outfit.get("items", []):
            k = self._key(item)
            if k is not None:
                keys.append(k)
        return set(keys)

    def _w(self, age):
        # age=0 most recent
        return float(math.exp(-float(age) / (self.tau + 1e-9)))

    def penalty(self, outfit):
        sig = self.outfit_signature(outfit)
        if not sig:
            return 0.0

        # ---- overlap penalty (recency-weighted)
        overlap_pen = 0.0
        for age, past_sig in enumerate(reversed(self.memory)):
            ov = len(sig & past_sig)
            if ov >= 3:
                overlap_pen = max(overlap_pen, self._w(age) * self.p3)
            elif ov == 2:
                overlap_pen = max(overlap_pen, self._w(age) * self.p2)
            elif ov == 1:
                overlap_pen = max(overlap_pen, self._w(age) * self.p1)

        # ---- item cooldown penalty (recency-weighted frequency)
        item_sum = 0.0
        for age, past_keys in enumerate(reversed(self.item_memory)):
            w = self._w(age)
            for k in sig:
                if k in past_keys:
                    item_sum += w

        item_pen = (item_sum / max(1, len(sig))) * self.w_item

        pen = min(self.max_penalty, overlap_pen + item_pen)
        return float(pen)

    def update(self, outfits):
        for o in outfits:
            sig = self.outfit_signature(o)
            self.memory.append(sig)
            self.item_memory.append(list(sig))
