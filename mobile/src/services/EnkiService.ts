/**
 * EnkiService — manages the Socket.IO connection to the Enki AI backend
 * and the WebSocket streams for raw PCM audio I/O.
 *
 * Glasses mode flow:
 *  1. Socket.IO connection to `http://<host>:8000`  — control plane
 *  2. WebSocket to `ws://<host>:8000/ws/audio-in`   — mic audio → Gemini
 *  3. WebSocket to `ws://<host>:8000/ws/audio-out`  — Gemini speech → glasses
 *  4. WebSocket to `ws://<host>:8000/ws/video-in`   — Ray-Ban camera → Gemini
 */

import { io, Socket } from 'socket.io-client';

export type TranscriptionMessage = { sender: 'User' | 'ADA'; text: string };
export type ConnectionStatus = 'disconnected' | 'connecting' | 'connected' | 'active';

export interface EnkiServiceCallbacks {
  onStatus?: (msg: string) => void;
  onTranscription?: (msg: TranscriptionMessage) => void;
  onAuthStatus?: (authenticated: boolean) => void;
  onError?: (msg: string) => void;
  onAudioData?: (data: number[]) => void;
  onConnectionChange?: (status: ConnectionStatus) => void;
}

class EnkiService {
  private socket: Socket | null = null;
  private audioInWs: WebSocket | null = null;
  private audioOutWs: WebSocket | null = null;
  private videoInWs: WebSocket | null = null;
  private callbacks: EnkiServiceCallbacks = {};
  private serverUrl: string = '';
  private _status: ConnectionStatus = 'disconnected';

  // ---------------------------------------------------------------------------
  // Connection lifecycle
  // ---------------------------------------------------------------------------

  connect(serverUrl: string, callbacks: EnkiServiceCallbacks): void {
    // Disconnect any existing connection before creating a new one
    if (this.socket?.connected) {
      this.socket.disconnect();
    }
    this.serverUrl = serverUrl.replace(/\/$/, '');
    this.callbacks = callbacks;
    this._setStatus('connecting');

    this.socket = io(this.serverUrl, {
      transports: ['websocket'],
      reconnectionAttempts: 5,
    });

    this.socket.on('connect', () => {
      console.log('[EnkiService] Socket.IO connected');
      this._setStatus('connected');
    });

    this.socket.on('disconnect', () => {
      console.log('[EnkiService] Socket.IO disconnected');
      this._setStatus('disconnected');
    });

    this.socket.on('connect_error', (err) => {
      console.error('[EnkiService] Connection error:', err.message);
      this.callbacks.onError?.(`Connection failed: ${err.message}`);
      this._setStatus('disconnected');
    });

    this.socket.on('status', (data: { msg: string }) => {
      console.log('[EnkiService] Status:', data.msg);
      this.callbacks.onStatus?.(data.msg);
      if (data.msg === 'Enki AI Started') {
        this._setStatus('active');
      }
    });

    this.socket.on('transcription', (data: TranscriptionMessage) => {
      this.callbacks.onTranscription?.(data);
    });

    this.socket.on('auth_status', (data: { authenticated: boolean }) => {
      this.callbacks.onAuthStatus?.(data.authenticated);
    });

    this.socket.on('audio_data', (data: { data: number[] }) => {
      this.callbacks.onAudioData?.(data.data);
    });

    this.socket.on('error', (data: { msg: string }) => {
      this.callbacks.onError?.(data.msg);
    });
  }

  disconnect(): void {
    this.stopAudio();
    this.closeWebSockets();
    this.socket?.disconnect();
    this.socket = null;
    this._setStatus('disconnected');
  }

  // ---------------------------------------------------------------------------
  // Enki AI session
  // ---------------------------------------------------------------------------

  startAudio(glassesMode: boolean = true): void {
    this.socket?.emit('start_audio', {
      glasses_mode: glassesMode,
      muted: false,
    });
  }

  stopAudio(): void {
    this.socket?.emit('stop_audio');
  }

  pauseAudio(): void {
    this.socket?.emit('pause_audio');
  }

  resumeAudio(): void {
    this.socket?.emit('resume_audio');
  }

  sendText(text: string): void {
    this.socket?.emit('user_input', { text });
  }

  /**
   * Kernel Panic — emits a `kernel_panic` event to the server, signalling
   * the Architect's intent to immediately reset the current AI session.
   */
  kernelPanic(): void {
    this.socket?.emit('kernel_panic', { reason: 'ARCHITECT_INITIATED' });
  }

  // ---------------------------------------------------------------------------
  // Raw PCM WebSocket streams
  // ---------------------------------------------------------------------------

  /**
   * Open the /ws/audio-in WebSocket.
   * After calling this, use sendAudioChunk() to stream microphone PCM.
   */
  openAudioInStream(): Promise<void> {
    return new Promise((resolve, reject) => {
      const wsUrl = this.serverUrl.replace(/^http/, 'ws') + '/ws/audio-in';
      this.audioInWs = new WebSocket(wsUrl);
      this.audioInWs.binaryType = 'arraybuffer';

      this.audioInWs.onopen = () => {
        console.log('[EnkiService] /ws/audio-in open');
        resolve();
      };

      this.audioInWs.onerror = (e) => {
        console.error('[EnkiService] /ws/audio-in error', e);
        reject(new Error('Failed to open audio-in WebSocket'));
      };

      this.audioInWs.onclose = () => {
        console.log('[EnkiService] /ws/audio-in closed');
      };
    });
  }

  /**
   * Open the /ws/audio-out WebSocket.
   * Received PCM bytes are delivered to onPcmReceived.
   */
  openAudioOutStream(onPcmReceived: (bytes: ArrayBuffer) => void): Promise<void> {
    return new Promise((resolve, reject) => {
      const wsUrl = this.serverUrl.replace(/^http/, 'ws') + '/ws/audio-out';
      this.audioOutWs = new WebSocket(wsUrl);
      this.audioOutWs.binaryType = 'arraybuffer';

      this.audioOutWs.onopen = () => {
        console.log('[EnkiService] /ws/audio-out open');
        resolve();
      };

      this.audioOutWs.onmessage = (event) => {
        onPcmReceived(event.data as ArrayBuffer);
      };

      this.audioOutWs.onerror = (e) => {
        console.error('[EnkiService] /ws/audio-out error', e);
        reject(new Error('Failed to open audio-out WebSocket'));
      };

      this.audioOutWs.onclose = () => {
        console.log('[EnkiService] /ws/audio-out closed');
      };
    });
  }

  /**
   * Open the /ws/video-in WebSocket for streaming Ray-Ban camera frames.
   * Frames should be raw JPEG bytes or base64-encoded JPEG strings.
   */
  openVideoInStream(): Promise<void> {
    return new Promise((resolve, reject) => {
      const wsUrl = this.serverUrl.replace(/^http/, 'ws') + '/ws/video-in';
      this.videoInWs = new WebSocket(wsUrl);
      this.videoInWs.binaryType = 'arraybuffer';

      this.videoInWs.onopen = () => {
        console.log('[EnkiService] /ws/video-in open');
        resolve();
      };

      this.videoInWs.onerror = (e) => {
        console.error('[EnkiService] /ws/video-in error', e);
        reject(new Error('Failed to open video-in WebSocket'));
      };

      this.videoInWs.onclose = () => {
        console.log('[EnkiService] /ws/video-in closed');
      };
    });
  }

  sendAudioChunk(pcmBytes: ArrayBuffer): void {
    if (this.audioInWs?.readyState === WebSocket.OPEN) {
      this.audioInWs.send(pcmBytes);
    }
  }

  sendVideoFrame(jpegBase64: string): void {
    if (this.videoInWs?.readyState === WebSocket.OPEN) {
      this.videoInWs.send(jpegBase64);
    }
  }

  closeWebSockets(): void {
    this.audioInWs?.close();
    this.audioOutWs?.close();
    this.videoInWs?.close();
    this.audioInWs = null;
    this.audioOutWs = null;
    this.videoInWs = null;
  }

  // ---------------------------------------------------------------------------
  // Helpers
  // ---------------------------------------------------------------------------

  get status(): ConnectionStatus {
    return this._status;
  }

  private _setStatus(s: ConnectionStatus): void {
    this._status = s;
    this.callbacks.onConnectionChange?.(s);
  }
}

// Singleton so all screens share the same connection
export const enkiService = new EnkiService();
