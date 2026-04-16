/**
 * AudioService — handles microphone recording and audio playback for the
 * Meta Ray-Ban companion app.
 *
 * Recording strategy
 * ------------------
 * expo-av does not expose a real-time PCM stream, so we use a rolling-chunk
 * approach:
 *   1. Start a short recording (~300 ms).
 *   2. Stop it, read the file as base64, strip the WAV header, send raw PCM.
 *   3. Immediately start the next recording.
 *
 * The Ray-Bans register as a standard Bluetooth HFP/HSP headset, so the OS
 * automatically routes AudioSession to them when they are the active device.
 * No special BT code is required — just set the correct AVAudioSession category
 * (playAndRecord + allowBluetooth) which expo-av handles.
 *
 * Playback strategy
 * -----------------
 * Received PCM chunks (16-bit LE, 24 kHz mono from Gemini) are written to a
 * temporary WAV file and played back in sequence via expo-av.
 *
 * Audio format contract with the backend
 * ---------------------------------------
 *  - Mic upload  : 16-bit signed PCM, 16 000 Hz, 1 channel  (ada.py SEND_SAMPLE_RATE)
 *  - Playback in : 16-bit signed PCM, 24 000 Hz, 1 channel  (ada.py RECEIVE_SAMPLE_RATE)
 */

import { Audio, AVPlaybackStatus } from 'expo-av';
import * as FileSystem from 'expo-file-system';

// WAV header constants
const SEND_SAMPLE_RATE = 16000;   // Must match ada.py SEND_SAMPLE_RATE
const RECV_SAMPLE_RATE = 24000;   // Must match ada.py RECEIVE_SAMPLE_RATE
const BIT_DEPTH = 16;
const CHANNELS = 1;

// How long each recording chunk is in ms.  Shorter = lower latency but more overhead.
const CHUNK_DURATION_MS = 300;

type PcmSendCallback = (pcmBytes: ArrayBuffer) => void;

export class AudioService {
  private recording: Audio.Recording | null = null;
  private isRecording = false;
  private onPcmChunk: PcmSendCallback | null = null;
  private playbackQueue: ArrayBuffer[] = [];
  private isPlaying = false;
  private sound: Audio.Sound | null = null;

  // ---------------------------------------------------------------------------
  // Permissions & session setup
  // ---------------------------------------------------------------------------

  async requestPermissions(): Promise<boolean> {
    const { status } = await Audio.requestPermissionsAsync();
    return status === 'granted';
  }

  async configureSession(): Promise<void> {
    await Audio.setAudioModeAsync({
      allowsRecordingIOS: true,
      // Routes audio to Bluetooth HFP headset (Ray-Bans) on iOS
      playsInSilentModeIOS: true,
      staysActiveInBackground: true,
      // On iOS, ALLOW_BLUETOOTH routes to HFP (mono, lower quality but lower latency)
      // Use allowsRecordingIOS + ALLOW_BLUETOOTH to enable BT mic and speaker
      interruptionModeIOS: 1, // DO_NOT_MIX
      interruptionModeAndroid: 1,
      shouldDuckAndroid: false,
    });
  }

  // ---------------------------------------------------------------------------
  // Recording
  // ---------------------------------------------------------------------------

  async startStreaming(onChunk: PcmSendCallback): Promise<void> {
    this.onPcmChunk = onChunk;
    this.isRecording = true;
    await this._recordChunkLoop();
  }

  stopStreaming(): void {
    this.isRecording = false;
    this.recording?.stopAndUnloadAsync().catch((err) => {
      console.warn('[AudioService] Error stopping recording:', err);
    });
    this.recording = null;
  }

  private async _recordChunkLoop(): Promise<void> {
    while (this.isRecording) {
      try {
        await this._recordOneChunk();
      } catch (err) {
        console.error('[AudioService] Recording error:', err);
        await new Promise((r) => setTimeout(r, 100));
      }
    }
  }

  private async _recordOneChunk(): Promise<void> {
    // Configure for 16-bit PCM at SEND_SAMPLE_RATE
    this.recording = new Audio.Recording();
    await this.recording.prepareToRecordAsync({
      android: {
        extension: '.wav',
        outputFormat: Audio.AndroidOutputFormat.DEFAULT,
        audioEncoder: Audio.AndroidAudioEncoder.DEFAULT,
        sampleRate: SEND_SAMPLE_RATE,
        numberOfChannels: CHANNELS,
        bitRate: SEND_SAMPLE_RATE * BIT_DEPTH * CHANNELS,
      },
      ios: {
        extension: '.wav',
        audioQuality: Audio.IOSAudioQuality.LOW,
        sampleRate: SEND_SAMPLE_RATE,
        numberOfChannels: CHANNELS,
        bitRate: SEND_SAMPLE_RATE * BIT_DEPTH * CHANNELS,
        linearPCMBitDepth: BIT_DEPTH,
        linearPCMIsBigEndian: false,
        linearPCMIsFloat: false,
      },
      web: {
        mimeType: 'audio/wav',
        bitsPerSecond: SEND_SAMPLE_RATE * BIT_DEPTH * CHANNELS,
      },
    });

    await this.recording.startAsync();
    await new Promise((r) => setTimeout(r, CHUNK_DURATION_MS));
    await this.recording.stopAndUnloadAsync();

    const uri = this.recording.getURI();
    this.recording = null;

    if (!uri) return;

    // Read the WAV file, strip the 44-byte header, send raw PCM
    const base64 = await FileSystem.readAsStringAsync(uri, {
      encoding: FileSystem.EncodingType.Base64,
    });
    await FileSystem.deleteAsync(uri, { idempotent: true });

    const wavBytes = _base64ToArrayBuffer(base64);
    const WAV_HEADER_SIZE = 44;
    if (wavBytes.byteLength <= WAV_HEADER_SIZE) return;

    const pcm = wavBytes.slice(WAV_HEADER_SIZE);
    this.onPcmChunk?.(pcm);
  }

  // ---------------------------------------------------------------------------
  // Playback
  // ---------------------------------------------------------------------------

  /**
   * Enqueue a raw PCM chunk received from the backend.
   * @param pcmBytes  16-bit LE PCM at RECV_SAMPLE_RATE (from Gemini via server)
   */
  enqueuePlayback(pcmBytes: ArrayBuffer): void {
    this.playbackQueue.push(pcmBytes);
    if (!this.isPlaying) {
      this._drainPlaybackQueue().catch(console.error);
    }
  }

  private async _drainPlaybackQueue(): Promise<void> {
    this.isPlaying = true;
    while (this.playbackQueue.length > 0) {
      const pcm = this.playbackQueue.shift()!;
      await this._playSingleChunk(pcm);
    }
    this.isPlaying = false;
  }

  private async _playSingleChunk(pcmBytes: ArrayBuffer): Promise<void> {
    try {
      // Build a minimal WAV file wrapping the raw PCM
      const wavBytes = _buildWav(pcmBytes, RECV_SAMPLE_RATE, CHANNELS, BIT_DEPTH);
      const base64 = _arrayBufferToBase64(wavBytes);
      const uri = FileSystem.cacheDirectory + `enki_play_${Date.now()}.wav`;

      await FileSystem.writeAsStringAsync(uri, base64, {
        encoding: FileSystem.EncodingType.Base64,
      });

      const { sound } = await Audio.Sound.createAsync(
        { uri },
        { shouldPlay: true, volume: 1.0 }
      );
      this.sound = sound;

      // Wait for playback to finish
      await new Promise<void>((resolve) => {
        sound.setOnPlaybackStatusUpdate((status: AVPlaybackStatus) => {
          if (!status.isLoaded) return;
          if (status.didJustFinish) {
            resolve();
          }
        });
      });

      await sound.unloadAsync();
      await FileSystem.deleteAsync(uri, { idempotent: true });
      this.sound = null;
    } catch (err) {
      console.error('[AudioService] Playback error:', err);
    }
  }

  stopPlayback(): void {
    this.playbackQueue = [];
    this.sound?.stopAsync().catch((err) => {
      console.warn('[AudioService] Error stopping sound:', err);
    });
    this.sound?.unloadAsync().catch((err) => {
      console.warn('[AudioService] Error unloading sound:', err);
    });
    this.sound = null;
    this.isPlaying = false;
  }

  cleanup(): void {
    this.stopStreaming();
    this.stopPlayback();
  }
}

// ---------------------------------------------------------------------------
// Utilities
// ---------------------------------------------------------------------------

function _base64ToArrayBuffer(base64: string): ArrayBuffer {
  const binary = atob(base64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i);
  }
  return bytes.buffer;
}

function _arrayBufferToBase64(buffer: ArrayBuffer): string {
  const bytes = new Uint8Array(buffer);
  let binary = '';
  for (let i = 0; i < bytes.byteLength; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary);
}

/**
 * Build a minimal valid WAV file wrapping raw PCM data.
 */
function _buildWav(
  pcmData: ArrayBuffer,
  sampleRate: number,
  numChannels: number,
  bitDepth: number
): ArrayBuffer {
  const pcmBytes = pcmData.byteLength;
  const byteRate = (sampleRate * numChannels * bitDepth) / 8;
  const blockAlign = (numChannels * bitDepth) / 8;
  const buffer = new ArrayBuffer(44 + pcmBytes);
  const view = new DataView(buffer);

  // RIFF header
  _writeString(view, 0, 'RIFF');
  view.setUint32(4, 36 + pcmBytes, true);
  _writeString(view, 8, 'WAVE');
  _writeString(view, 12, 'fmt ');
  view.setUint32(16, 16, true);          // PCM sub-chunk size
  view.setUint16(20, 1, true);           // PCM format
  view.setUint16(22, numChannels, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, byteRate, true);
  view.setUint16(32, blockAlign, true);
  view.setUint16(34, bitDepth, true);
  _writeString(view, 36, 'data');
  view.setUint32(40, pcmBytes, true);

  // PCM data
  const src = new Uint8Array(pcmData);
  const dst = new Uint8Array(buffer, 44);
  dst.set(src);

  return buffer;
}

function _writeString(view: DataView, offset: number, str: string): void {
  for (let i = 0; i < str.length; i++) {
    view.setUint8(offset + i, str.charCodeAt(i));
  }
}

export const audioService = new AudioService();
