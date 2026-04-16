"""
GestureController — MediaPipe-based hand gesture detection for the Enki AI
spatial-interaction pipeline.

Detects four gesture classes from RGB video frames:
  PINCH        — thumb tip close to index-finger tip (< 0.05 normalised units)
  STRETCH      — thumb + majority of fingers extended outward
  SHIELD_PALM  — all four fingers fully extended (open palm)
  FIST         — all fingers curled

When a gesture is identified the controller emits a structured JSON-compatible
dict and logs the decision to the GovernanceEngine audit trail (L06 –
Transparency).  Every call is wrapped in a broad try/except so that a poorly-
lit frame ("the light on the Meadows is too low") never causes a Kernel Panic.
"""

from __future__ import annotations

import math
import os
import sys
from typing import Optional

# Make the enki_ai package importable when running from backend/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from enki_ai.core.governance import engine as governance_engine

# ---------------------------------------------------------------------------
# Gesture constants
# ---------------------------------------------------------------------------

GESTURE_PINCH = "PINCH"
GESTURE_STRETCH = "STRETCH"
GESTURE_SHIELD_PALM = "SHIELD_PALM"
GESTURE_FIST = "FIST"
GESTURE_NONE = "NONE"

# Distance threshold (normalised landmark space) below which thumb–index
# proximity counts as a pinch.
_PINCH_THRESHOLD = 0.05


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------


def _euclidean(p1, p2) -> float:
    """Return Euclidean distance between two normalised MediaPipe landmarks."""
    return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)


# ---------------------------------------------------------------------------
# GestureController
# ---------------------------------------------------------------------------


class GestureController:
    """
    Stateful hand-gesture detector backed by MediaPipe Hands.

    Typical usage::

        controller = GestureController()
        packet = controller.process_frame(rgb_frame)
        if packet and packet["gesture"] == GESTURE_PINCH:
            ...
        controller.close()

    The controller is intentionally single-threaded.  If you need concurrent
    frame processing, create one instance per thread/coroutine.
    """

    def __init__(self) -> None:
        import mediapipe as mp

        self._mp_hands = mp.solutions.hands
        self._hands = self._mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def process_frame(self, frame_rgb) -> Optional[dict]:
        """
        Analyse one RGB frame (numpy H×W×3 uint8 array).

        Returns a dict on success::

            {
                "gesture":    str,    # one of the GESTURE_* constants
                "x":          float,  # normalised wrist X  (0–1, left→right)
                "y":          float,  # normalised wrist Y  (0–1, top→bottom)
                "confidence": float,  # placeholder, always 1.0 when detected
            }

        Returns ``None`` if no hand was detected or if the frame is unusable
        (too dark, motion blur, etc.) — the exception is caught internally so
        the caller's event loop is never interrupted.
        """
        try:
            results = self._hands.process(frame_rgb)

            if not results.multi_hand_landmarks:
                return None

            # Process only the first (dominant) hand
            hand_landmarks = results.multi_hand_landmarks[0]
            lm = hand_landmarks.landmark

            gesture = self._classify_gesture(lm)

            # Use wrist landmark (index 0) as the representative coordinate.
            x = float(lm[0].x)
            y = float(lm[0].y)

            packet: dict = {
                "gesture": gesture,
                "x": round(x, 4),
                "y": round(y, 4),
                "confidence": 1.0,
            }

            if gesture != GESTURE_NONE:
                governance_engine.log_decision(
                    action=f"spatial_gesture_{gesture.lower()}",
                    rationale=(
                        f"GestureController detected {gesture} at "
                        f"normalised coordinates ({x:.3f}, {y:.3f})."
                    ),
                    human_reviewed=False,
                    context={"gesture": gesture, "x": x, "y": y},
                )

            return packet

        except Exception as exc:
            # Low-light or corrupt frame — do not crash the pipeline.
            print(
                f"[GestureController] Frame processing error (kernel-safe): {exc}"
            )
            return None

    def close(self) -> None:
        """Release MediaPipe Hands resources."""
        try:
            self._hands.close()
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _classify_gesture(self, lm) -> str:
        """
        Map MediaPipe landmark positions to a named gesture.

        Landmark indices used:
          0  — wrist
          3  — thumb IP        4  — thumb tip
          5  — index MCP       6  — index PIP      8  — index tip
          10 — middle PIP      12 — middle tip
          14 — ring PIP        16 — ring tip
          17 — pinky MCP       18 — pinky PIP      20 — pinky tip
        """
        # ---- Finger-extension flags ----
        # A finger is "extended" when its tip is higher (smaller y) than its PIP.
        index_up = lm[8].y < lm[6].y
        middle_up = lm[12].y < lm[10].y
        ring_up = lm[16].y < lm[14].y
        pinky_up = lm[20].y < lm[18].y

        # Thumb: direction depends on which side the hand is on.
        thumb_up = (
            lm[4].x < lm[3].x
            if lm[5].x > lm[17].x
            else lm[4].x > lm[3].x
        )

        fingers_extended = sum([index_up, middle_up, ring_up, pinky_up])

        # ---- PINCH: thumb tip close to index tip ----
        if _euclidean(lm[4], lm[8]) < _PINCH_THRESHOLD:
            return GESTURE_PINCH

        # ---- FIST: all four fingers curled ----
        if fingers_extended == 0:
            return GESTURE_FIST

        # ---- SHIELD_PALM: all four fingers extended (open palm) ----
        if fingers_extended == 4:
            return GESTURE_SHIELD_PALM

        # ---- STRETCH: thumb + most fingers fully extended ----
        if fingers_extended >= 3 and thumb_up:
            return GESTURE_STRETCH

        return GESTURE_NONE
