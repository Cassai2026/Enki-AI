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
import time
from typing import Optional

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
# Privacy Lock — L03 (No Silent Profiling) hardware-level enforcement
# ---------------------------------------------------------------------------

# Global flag: when True, server.py MUST stop forwarding frames to Gemini.
privacy_lock: bool = False

# Timestamp (seconds since epoch) when a FIST gesture was first detected while
# the privacy lock is active.  None if no FIST is currently held.
_fist_start_time: Optional[float] = None

# Duration (seconds) of a sustained FIST gesture required to unlock.
FIST_UNLOCK_DURATION: float = 2.0


def is_privacy_locked() -> bool:
    """Return the current privacy lock state."""
    return privacy_lock


def set_privacy_lock(state: bool) -> None:
    """Explicitly set the privacy lock state (used in tests / overrides)."""
    global privacy_lock, _fist_start_time
    privacy_lock = state
    if not state:
        _fist_start_time = None


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
                "privacy_lock_active": bool,  # current privacy lock state
            }

        Returns ``None`` if no hand was detected or if the frame is unusable
        (too dark, motion blur, etc.) — the exception is caught internally so
        the caller's event loop is never interrupted.

        Privacy Lock (L03 — No Silent Profiling)
        ----------------------------------------
        * SHIELD_PALM activates ``privacy_lock`` immediately.
        * FIST held for ``FIST_UNLOCK_DURATION`` seconds while the lock is
          active deactivates it.
        """
        global privacy_lock, _fist_start_time

        try:
            results = self._hands.process(frame_rgb)

            if not results.multi_hand_landmarks:
                # Reset the FIST timer if the hand leaves the frame.
                _fist_start_time = None
                return None

            # Process only the first (dominant) hand
            hand_landmarks = results.multi_hand_landmarks[0]
            lm = hand_landmarks.landmark

            gesture = self._classify_gesture(lm)

            # Use wrist landmark (index 0) as the representative coordinate.
            x = float(lm[0].x)
            y = float(lm[0].y)

            # ------------------------------------------------------------------
            # Privacy Lock logic
            # ------------------------------------------------------------------
            if gesture == GESTURE_SHIELD_PALM and not privacy_lock:
                privacy_lock = True
                _fist_start_time = None
                governance_engine.log_decision(
                    action="privacy_lock_activated",
                    rationale=(
                        "SHIELD_PALM detected — privacy_lock engaged. "
                        "Gemini frame forwarding suspended (L03)."
                    ),
                    human_reviewed=True,
                    context={"gesture": gesture, "x": x, "y": y},
                )
                print("[GestureController] PRIVACY LOCK ACTIVATED (SHIELD_PALM)")

            elif gesture == GESTURE_FIST and privacy_lock:
                now = time.monotonic()
                if _fist_start_time is None:
                    _fist_start_time = now
                elif now - _fist_start_time >= FIST_UNLOCK_DURATION:
                    privacy_lock = False
                    _fist_start_time = None
                    governance_engine.log_decision(
                        action="privacy_lock_deactivated",
                        rationale=(
                            f"FIST held for {FIST_UNLOCK_DURATION}s — "
                            "privacy_lock released (L03)."
                        ),
                        human_reviewed=True,
                        context={"gesture": gesture, "x": x, "y": y},
                    )
                    print("[GestureController] PRIVACY LOCK DEACTIVATED (FIST 2s)")
            else:
                # Any gesture other than FIST resets the FIST hold timer.
                if gesture != GESTURE_FIST:
                    _fist_start_time = None

            packet: dict = {
                "gesture": gesture,
                "x": round(x, 4),
                "y": round(y, 4),
                "confidence": 1.0,
                "privacy_lock_active": privacy_lock,
            }

            if gesture != GESTURE_NONE:
                governance_engine.log_decision(
                    action=f"spatial_gesture_{gesture.lower()}",
                    rationale=(
                        f"GestureController detected {gesture} at "
                        f"normalised coordinates ({x:.3f}, {y:.3f})."
                    ),
                    human_reviewed=False,
                    context={
                        "gesture": gesture,
                        "x": x,
                        "y": y,
                        "privacy_lock_active": privacy_lock,
                    },
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
