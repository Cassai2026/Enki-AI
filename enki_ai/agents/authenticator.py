import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision
import cv2
import asyncio
import os
import base64
import numpy as np
import urllib.request

# Default registry directory — one level above the package root so that
# biometric assets are not stored inside the Python package tree.
_DEFAULT_REGISTRY_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "auth",
    "registry",
)

# Supported image extensions for the registry scan.
_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}


class FaceAuthenticator:
    # MediaPipe Face Landmarker model URL
    MODEL_URL = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
    MODEL_PATH = os.path.join(os.path.dirname(__file__), "face_landmarker.task")

    def __init__(
        self,
        registry_dir=None,
        reference_image_path=None,
        on_status_change=None,
        on_frame=None,
    ):
        """
        Initialise the authenticator.

        :param registry_dir: Directory containing authorised user photos
            (``auth/registry/`` by default).  Every ``.jpg``/``.png`` file is
            loaded as one authorised identity.
        :param reference_image_path: Deprecated single-file path kept for
            backwards compatibility.  If *registry_dir* is ``None`` and this
            argument is provided, the file is treated as a one-entry registry.
        :param on_status_change: Async callback(is_authenticated: bool).
        :param on_frame: Async callback(frame_data_b64: str) for live frames.
        """
        # Resolve registry directory.
        if registry_dir is not None:
            self.registry_dir = registry_dir
            self._legacy_reference_path = None
        elif reference_image_path is not None:
            # Backwards-compat: wrap a single file path.
            self.registry_dir = None
            self._legacy_reference_path = reference_image_path
        else:
            self.registry_dir = _DEFAULT_REGISTRY_DIR
            self._legacy_reference_path = None

        # Keep the old attribute so existing tests that read it don't break.
        self.reference_image_path = reference_image_path or os.path.join(
            os.path.dirname(__file__), "reference.jpg"
        )

        self.on_status_change = on_status_change
        self.on_frame = on_frame

        self.authenticated = False
        self.running = False
        # Maps username → landmark vector for every enrolled user.
        self._registry: dict = {}
        # Legacy single-reference slot kept for backwards compat.
        self.reference_landmarks = None
        self.landmarker = None

        self._ensure_model()
        self._init_landmarker()
        self._load_registry()

    def _ensure_model(self):
        """Download the MediaPipe Face Landmarker model if not present."""
        if not os.path.exists(self.MODEL_PATH):
            print(f"[AUTH] Downloading Face Landmarker model...")
            try:
                urllib.request.urlretrieve(self.MODEL_URL, self.MODEL_PATH)
                print(f"[AUTH] [OK] Model downloaded to {self.MODEL_PATH}")
            except Exception as e:
                print(f"[AUTH] [ERR] Failed to download model: {e}")

    def _init_landmarker(self):
        """Initialize the MediaPipe Face Landmarker."""
        if not os.path.exists(self.MODEL_PATH):
            print("[AUTH] [ERR] Face Landmarker model not found. Cannot initialize.")
            return
        
        try:
            base_options = mp_python.BaseOptions(model_asset_path=self.MODEL_PATH)
            options = vision.FaceLandmarkerOptions(
                base_options=base_options,
                output_face_blendshapes=False,
                output_facial_transformation_matrixes=False,
                num_faces=1
            )
            self.landmarker = vision.FaceLandmarker.create_from_options(options)
            print("[AUTH] [OK] Face Landmarker initialized.")
        except Exception as e:
            print(f"[AUTH] [ERR] Failed to initialize Face Landmarker: {e}")

    def _extract_landmarks(self, image_rgb):
        """
        Extract normalized face landmarks from an RGB image.
        Returns a flattened numpy array of (x, y, z) coordinates, or None if no face found.
        """
        if self.landmarker is None:
            return None
        
        try:
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
            result = self.landmarker.detect(mp_image)
            
            if result.face_landmarks and len(result.face_landmarks) > 0:
                landmarks = result.face_landmarks[0]
                # Convert to numpy array of (x, y, z) coordinates
                coords = np.array([[lm.x, lm.y, lm.z] for lm in landmarks], dtype=np.float32)
                return coords.flatten()
            return None
        except Exception as e:
            print(f"[AUTH] [ERR] Landmark extraction failed: {e}")
            return None

    def _compare_landmarks(self, landmarks1, landmarks2, threshold=0.15):
        """
        Compare two landmark vectors using cosine similarity.
        Returns True if similarity is above (1 - threshold).
        """
        if landmarks1 is None or landmarks2 is None:
            return False
        
        # Normalize vectors
        norm1 = np.linalg.norm(landmarks1)
        norm2 = np.linalg.norm(landmarks2)
        
        if norm1 == 0 or norm2 == 0:
            return False
        
        # Cosine similarity
        similarity = np.dot(landmarks1, landmarks2) / (norm1 * norm2)
        
        # Threshold check (similarity should be close to 1 for a match)
        is_match = similarity > (1 - threshold)
        if is_match:
            print(f"[AUTH] Face match! Similarity: {similarity:.4f}")
        return is_match

    def _load_registry(self):
        """
        Populate ``self._registry`` from the registry directory (or the legacy
        single-file path).  Each loaded entry maps a user name to a landmark
        vector extracted by ``_extract_landmarks``.
        """
        candidates: list[tuple[str, str]] = []  # (username, filepath)

        if self._legacy_reference_path is not None:
            # Single-file backwards-compat path.
            candidates.append(("default", self._legacy_reference_path))
        elif self.registry_dir is not None:
            if not os.path.isdir(self.registry_dir):
                print(
                    f"[AUTH] [WARN] Registry directory not found: {self.registry_dir}. "
                    "Authentication will fail until users are enrolled."
                )
                return
            for fname in sorted(os.listdir(self.registry_dir)):
                ext = os.path.splitext(fname)[1].lower()
                if ext in _IMAGE_EXTENSIONS:
                    username = os.path.splitext(fname)[0]
                    candidates.append((username, os.path.join(self.registry_dir, fname)))

        if not candidates:
            print("[AUTH] [WARN] No face images found in registry. Authentication will fail.")
            return

        for username, path in candidates:
            if not os.path.exists(path):
                print(f"[AUTH] [WARN] Registry image not found: {path}")
                continue
            try:
                img_bgr = cv2.imread(path)
                if img_bgr is None:
                    print(f"[AUTH] [ERR] Failed to read image: {path}")
                    continue
                image_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
                landmarks = self._extract_landmarks(image_rgb)
                if landmarks is not None:
                    self._registry[username] = landmarks
                    print(f"[AUTH] [OK] Enrolled user '{username}' from {os.path.basename(path)}")
                else:
                    print(f"[AUTH] [ERR] No face found in {path} — user '{username}' not enrolled.")
            except Exception as exc:
                print(f"[AUTH] [ERR] Error loading {path}: {exc}")

        # Backwards-compat: expose the first loaded entry as reference_landmarks
        if self._registry:
            self.reference_landmarks = next(iter(self._registry.values()))
            print(f"[AUTH] Registry loaded: {len(self._registry)} user(s) enrolled.")
        else:
            print("[AUTH] [WARN] Registry is empty after loading. Authentication will fail.")

    # ------------------------------------------------------------------
    # Legacy method kept for backwards compatibility with existing callers.
    # ------------------------------------------------------------------
    def _load_reference(self):
        """Deprecated wrapper — delegates to _load_registry."""
        self._load_registry()

    def _pulse_matches_registry(self, current_landmarks) -> tuple[bool, str]:
        """
        Verify the Animus pulse (current face landmarks) against **all**
        authorised users in the registry.

        Returns ``(True, username)`` on the first match, or ``(False, "")``
        if no match is found.
        """
        for username, ref_landmarks in self._registry.items():
            if self._compare_landmarks(ref_landmarks, current_landmarks):
                return True, username
        return False, ""

    async def start_authentication_loop(self):
        if self.authenticated:
            print("[AUTH] Already authenticated.")
            if self.on_status_change:
                await self.on_status_change(True)
            return

        if not self._registry:
             print("[AUTH] [ERR] Cannot start auth loop: No users enrolled in registry.")
             return

        self.running = True
        print(f"[AUTH] Starting camera — verifying against {len(self._registry)} enrolled user(s).")
        
        # Capture the current (main) event loop
        loop = asyncio.get_running_loop()
        
        # Use a separate thread for blocking camera/CV operations
        await asyncio.to_thread(self._run_cv_loop, loop)

        print("[AUTH] Authentication loop finished.")
    
    def stop(self):
        print("[AUTH] Stopping authentication loop...")
        self.running = False

    def _run_cv_loop(self, loop):
        def try_open_camera(index):
            print(f"[AUTH] Trying to open camera with index {index}...")
            cap = cv2.VideoCapture(index, cv2.CAP_AVFOUNDATION)
            if not cap.isOpened():
                print(f"[AUTH] [ERR] Could not open video device {index}.")
                return None
            
            ret, frame = cap.read()
            if not ret:
                 print(f"[AUTH] [ERR] Opened device {index} but failed to read first frame.")
                 cap.release()
                 return None
            
            print(f"[AUTH] [OK] Successfully opened and read from device {index}.")
            return cap

        video_capture = try_open_camera(0)
        
        if video_capture is None:
             print("[AUTH] Device 0 failed. Trying device 1...")
             video_capture = try_open_camera(1)

        if video_capture is None:
             print("[AUTH] [ERR] All camera attempts failed. Authentication cannot proceed.")
             self.running = False
             return

        process_this_frame = True
        
        while self.running and not self.authenticated:
            ret, frame = video_capture.read()
            if not ret:
                print("[AUTH] [ERR] Failed to read frame from camera loop.")
                break
            
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process every other frame for performance
            if process_this_frame:
                current_landmarks = self._extract_landmarks(rgb_frame)
                
                matched, username = self._pulse_matches_registry(current_landmarks)
                if matched:
                    self.authenticated = True
                    print(f"[AUTH] [OPEN] FACE RECOGNIZED — user '{username}'. Access Granted.")
                    if self.on_status_change:
                        asyncio.run_coroutine_threadsafe(self.on_status_change(True), loop)
                    self.running = False
                    break

            process_this_frame = not process_this_frame

            # Send frame to frontend if callback exists
            if self.on_frame:
                small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
                _, buffer = cv2.imencode('.jpg', small_frame)
                b64_str = base64.b64encode(buffer).decode('utf-8')
                
                asyncio.run_coroutine_threadsafe(self.on_frame(b64_str), loop)

        video_capture.release()
