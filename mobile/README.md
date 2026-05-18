# Enki AI — Meta Ray-Ban Companion App

React Native (Expo) mobile app that bridges your **Meta Ray-Ban smart glasses** to the Enki AI backend.

## MVP scope (locked for today)

Core flow only:
- Connect to a backend URL
- Start/stop a live audio session
- Stream mic PCM to Enki and play returned PCM through glasses
- Show live transcription and actionable connection/session errors
- Recover with in-app retry/reconnect controls

Out of scope for today:
- Wake-word engine integration
- Production analytics backend
- Camera-based vision shipping flow (endpoint is ready, integration remains optional)

## Target platforms (today)

- iOS
- Android

## Version notes

- `1.1.0`: MVP hardening release (env strategy, onboarding retry/recovery UX, reconnect handling, telemetry hooks, EAS build profile scaffolding, and updated release runbook).

## How it works

```
Ray-Bans (BT headset)
       │  mic audio / speaker
       ▼
  iPhone / Android  ◄──── Socket.IO ────► backend/server.py ──► Gemini Live API
       │                WebSocket (PCM)
       └─── ws/audio-in  ──►  Enki backend  (mic PCM → Gemini)
       ◄─── ws/audio-out ◄──  Enki backend  (Gemini speech → glasses)
       └─── ws/video-in  ──►  Enki backend  (Ray-Ban camera → Gemini)
```

The Ray-Bans register with your phone as a standard Bluetooth HFP/HSP headset.  iOS and Android automatically route microphone input and speaker output through them — no special Bluetooth code is needed in the app.

---

## Prerequisites

1. **Meta Ray-Ban glasses** paired with your phone via Bluetooth (through the Meta View app).
2. **Enki AI backend** running on a desktop/laptop on the same Wi-Fi network:
   ```bash
   conda activate enki-ai
   python backend/server.py
   ```
3. **Node.js 18+** and the **Expo Go** app (or a development build).

---

## Setup

```bash
# From the repo root
cd mobile
npm install
cp .env.example .env
npx expo start
```

Scan the QR code with **Expo Go** on your phone.

---

## First Run

1. Enter the backend server URL (e.g. `http://192.168.1.100:8000`) — your desktop's local IP.
2. Tap **Connect**.
3. Tap **▶ Start Session**.
4. Speak through your Ray-Bans — Ada responds through the glasses speakers.
5. If connect/start fails, use **Retry** or **Reconnect Backend** from the app UI.

## Connectivity assumptions for real-device testing

- Phone and backend machine must be on the same LAN/Wi-Fi.
- Backend must be reachable from phone over `http://<lan-ip>:8000`.
- If backend enforces `X-Sovereign-Token`, set `EXPO_PUBLIC_SOVEREIGN_TOKEN` in `.env`.
- Bluetooth pairing is OS-managed: Ray-Bans must be paired before starting session.

---

## Glasses-Mode Backend API

When the companion app calls `start_audio` with `{ glasses_mode: true }`, the backend:

| Endpoint | Direction | Description |
|---|---|---|
| `Socket.IO connect` | App → Server | Control-plane connection (`websocket` transport) |
| `Socket.IO start_audio` | App → Server | Starts Gemini Live session with network audio source |
| `Socket.IO pause_audio` / `resume_audio` / `stop_audio` | App → Server | Session controls |
| `Socket.IO signal_distortion` | App → Server | Notifies backend about elevated latency/jitter |
| `ws://<host>:8000/ws/audio-in` | App → Server | Raw 16-bit PCM @ 16 kHz (mic from Ray-Bans) |
| `ws://<host>:8000/ws/audio-out` | Server → App | Raw 16-bit PCM @ 24 kHz (Gemini speech output) |
| `ws://<host>:8000/ws/video-in` | App → Server | JPEG frames from Ray-Ban camera (base64 or raw bytes) |
| `Socket.IO transcription` | Server → App | Live conversation text |
| `Socket.IO audio_data` | Server → App | Duplicate audio path via Socket.IO (for debugging) |

Security note:
- If backend `SOVEREIGN_TOKEN` is set, mobile must send `X-Sovereign-Token` for secured WebSocket endpoints.

## Environment strategy

The app supports environment-scoped defaults via `.env`:

- `EXPO_PUBLIC_ENKI_ENV=dev|staging|prod`
- `EXPO_PUBLIC_ENKI_BACKEND_URL_DEV`
- `EXPO_PUBLIC_ENKI_BACKEND_URL_STAGING`
- `EXPO_PUBLIC_ENKI_BACKEND_URL_PROD`
- `EXPO_PUBLIC_SOVEREIGN_TOKEN` (optional; do not hardcode secrets in source)

The connect screen now:
- Prefills saved URL when available
- Falls back to environment default URL
- Validates URL format before connect
- Shows explicit retry path on failures

---

## Architecture notes

### Audio streaming
`AudioService.ts` records audio in 300 ms WAV chunks, strips the 44-byte WAV header, and sends raw PCM over the `/ws/audio-in` WebSocket.  Received PCM from `/ws/audio-out` is wrapped back into a WAV file on-the-fly and played via `expo-av`.

### Bluetooth routing
`audioService.configureSession()` calls `expo-av`'s `Audio.setAudioModeAsync` with:
- `allowsRecordingIOS: true`
- `staysActiveInBackground: true`
- `playsInSilentModeIOS: true`

This sets the correct `AVAudioSession` category on iOS so the OS routes audio to/from the paired Ray-Bans automatically.

### Camera (Phase 3)
The `/ws/video-in` endpoint is ready on the backend.  When Meta releases a public camera API for Ray-Bans (or via Meta AI Studio partner access), the app can send JPEG frames using `enkiService.sendVideoFrame(base64Jpeg)`.

---

## Adding Wake-Word Detection (Phase 2+)

The current implementation streams audio continuously while the session is active.  To add a true wake word ("Hey Enki"):

1. Install [`@picovoice/porcupine-react-native`](https://github.com/Picovoice/porcupine) — works offline, no cloud round-trip.
2. Create a custom "Hey Enki" wake word via the [Picovoice Console](https://console.picovoice.ai/).
3. In `ActiveScreen.tsx`, start `audioService.startStreaming()` only after Porcupine detects the wake word, and stop it after a silence timeout.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| Can't connect | Ensure phone and server are on the same Wi-Fi. Check `GEMINI_API_KEY` is set in `.env` on the server. |
| No audio through glasses | Make sure Ray-Bans are connected as the active Bluetooth device before tapping Start. |
| Echo / feedback | Lower volume on Ray-Bans or enable `muted: true` on start and unmute manually. |
| High latency | Reduce `CHUNK_DURATION_MS` in `AudioService.ts` (default 300 ms). Trade-off: more CPU. |

## Privacy and compliance essentials

- Microphone and Bluetooth permission strings are declared in `app.json`.
- The app presents a data-flow disclosure on the connect screen.
- Audio/video data is sent only to the configured Enki backend URL.
- Store production secrets in EAS/CI secrets management, not in committed files.

## Release runbook (internal testing → release candidate)

1. Run real-device smoke tests on at least one iPhone and one Android device.
2. Fix launch-blocking bugs only.
3. Build internal binaries with EAS preview profiles.
4. Collect tester feedback and prioritize launch blockers.
5. Cut RC builds and run final regression pass.
6. Submit to TestFlight / Play Internal Testing.
7. Monitor connect/session stability and crash reports after rollout.
