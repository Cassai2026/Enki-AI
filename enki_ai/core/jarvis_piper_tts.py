"""
Piper TTS helper utilities for JARVIS.

This module provides WAV volume reduction and a standalone Piper TTS
``speak()`` function.  In most cases you should use the ``speak()`` from
``enki_ai.core.jarvis_core`` instead; this module is kept as a lower-level
utility that does not depend on the full JARVIS runtime.
"""

import logging
import os
import subprocess
import tempfile
import time
import threading
from pathlib import Path
from typing import Optional

from enki_ai.core import config

log = logging.getLogger(__name__)


def reduce_wav_volume(
    infile: str,
    outfile: Optional[str] = None,
    gain: float = 0.5,
) -> str:
    """
    Reduce the volume of *infile* by *gain* (0.0–1.0) and write to *outfile*.

    Returns the path of the output file.
    """
    try:
        import numpy as np  # type: ignore[import]
        import soundfile as sf  # type: ignore[import]
    except ImportError as exc:
        raise ImportError("numpy and soundfile are required for WAV processing.") from exc

    infile_p = Path(infile)
    outfile_p = (
        Path(outfile)
        if outfile is not None
        else infile_p.with_name(infile_p.stem + "_low.wav")
    )

    data, sample_rate = sf.read(str(infile_p), dtype="float32")
    data *= float(max(0.0, min(1.0, gain)))
    data = np.clip(data, -1.0, 1.0)
    sf.write(str(outfile_p), data, sample_rate, subtype="PCM_16")
    return str(outfile_p)


def speak(text: str, voice_name: Optional[str] = None) -> None:
    """Synthesise *text* with Piper and play the resulting WAV."""
    piper_exe = str(config.PIPER_EXE)
    voice = voice_name or config.PIPER_VOICE
    model = str(config.PIPER_DIR / "voices" / f"{voice}.onnx")

    if not os.path.exists(piper_exe):
        log.warning("Piper not found at %s – skipping TTS.", piper_exe)
        return
    if not os.path.exists(model):
        log.warning("Piper model not found at %s – skipping TTS.", model)
        return

    try:
        fd, wav_path = tempfile.mkstemp(suffix=".wav")
        os.close(fd)

        cmd = [
            piper_exe,
            "--model", model,
            "--output_file", wav_path,
            "--length_scale", "1.2",
            "--noise_scale", "0.3",
            "--noise_w", "0.3",
        ]
        subprocess.run(
            cmd,
            input=text,
            text=True,
            check=True,
            cwd=str(config.PIPER_DIR),
            timeout=15,
        )

        if not os.path.exists(wav_path):
            log.error("Piper did not produce a WAV file at %s.", wav_path)
            return

        # Async playback
        def _play(path: str) -> None:
            try:
                import winsound  # type: ignore[import]
                winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)
            except ImportError:
                try:
                    subprocess.Popen(["aplay", path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except FileNotFoundError:
                    pass

        threading.Thread(target=_play, args=(wav_path,), daemon=True).start()

        def _cleanup(p: str) -> None:
            time.sleep(3.0)
            try:
                os.remove(p)
            except OSError:
                pass

        threading.Thread(target=_cleanup, args=(wav_path,), daemon=True).start()

    except subprocess.TimeoutExpired:
        log.error("Piper TTS timed out.")
    except subprocess.CalledProcessError as exc:
        log.error("Piper returned error: %s", exc)
    except Exception as exc:
        log.error("speak() error: %s", exc)
