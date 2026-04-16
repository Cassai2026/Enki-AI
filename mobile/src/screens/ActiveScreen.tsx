/**
 * ActiveScreen — the main session screen shown after connecting to the backend.
 *
 * Interaction model (glasses-optimised)
 * --------------------------------------
 *  • "Start Session" — calls start_audio with glasses_mode=true, opens the
 *    audio WebSocket streams, and begins continuous mic streaming.
 *  • "Stop" — tears everything down gracefully.
 *  • Wake-word shortcut — a long-press anywhere on the screen pauses/resumes the
 *    mic stream, simulating the Ray-Ban frame double-tap gesture.
 *  • Transcription log — shows the live conversation so the user can glance at
 *    their phone to verify what Ada heard/said.
 *
 * Audio routing
 * -------------
 * When Ray-Bans are paired and connected as a Bluetooth headset the OS
 * routes audio automatically.  No extra BT code is needed: expo-av uses the
 * active AVAudioSession route on iOS / AudioManager on Android.
 */

import React, { useCallback, useEffect, useRef, useState } from 'react';
import {
  Alert,
  FlatList,
  Platform,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import { audioService } from '../services/AudioService';
import { enkiService, TranscriptionMessage } from '../services/EnkiService';

interface Props {
  serverUrl: string;
  onDisconnect: () => void;
}

type SessionState = 'idle' | 'starting' | 'active' | 'stopping';

export default function ActiveScreen({ serverUrl, onDisconnect }: Props) {
  const [sessionState, setSessionState] = useState<SessionState>('idle');
  const [muted, setMuted] = useState(false);
  const [statusMsg, setStatusMsg] = useState('Ready');
  const [transcripts, setTranscripts] = useState<TranscriptionMessage[]>([]);
  const flatListRef = useRef<FlatList<TranscriptionMessage>>(null);

  // Stable callback for sending mic audio chunks to the backend
  const sendAudioChunk = useCallback(
    (pcm: ArrayBuffer) => enkiService.sendAudioChunk(pcm),
    []
  );

  // ---------------------------------------------------------------------------
  // Mount: wire up EnkiService callbacks
  // ---------------------------------------------------------------------------
  useEffect(() => {
    enkiService['callbacks'] = {
      onStatus: (msg) => setStatusMsg(msg),
      onTranscription: (msg) => {
        setTranscripts((prev) => [...prev, msg]);
        // Auto-scroll
        setTimeout(() => flatListRef.current?.scrollToEnd({ animated: true }), 80);
      },
      onError: (msg) => {
        Alert.alert('Enki Error', msg);
        setStatusMsg(`Error: ${msg}`);
      },
      onConnectionChange: (s) => {
        if (s === 'disconnected') {
          setSessionState('idle');
          setStatusMsg('Disconnected');
        }
      },
    };

    return () => {
      // Cleanup on unmount
      handleStop();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // ---------------------------------------------------------------------------
  // Session controls
  // ---------------------------------------------------------------------------

  const handleStart = useCallback(async () => {
    setSessionState('starting');
    setStatusMsg('Starting session…');

    try {
      // 1. Request mic permissions
      const granted = await audioService.requestPermissions();
      if (!granted) {
        Alert.alert('Permission Required', 'Microphone permission is required.');
        setSessionState('idle');
        return;
      }

      // 2. Configure audio session for Bluetooth routing
      await audioService.configureSession();

      // 3. Tell the backend to start in glasses mode
      enkiService.startAudio(true);

      // 4. Open the raw PCM WebSocket streams
      await enkiService.openAudioOutStream((pcmBytes) => {
        audioService.enqueuePlayback(pcmBytes);
      });
      await enkiService.openAudioInStream();

      // 5. Start continuous mic streaming
      audioService.startStreaming(sendAudioChunk);

      setSessionState('active');
      setStatusMsg('Listening via Ray-Bans…');
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      Alert.alert('Start Failed', msg);
      setSessionState('idle');
      setStatusMsg('Ready');
    }
  }, []);

  const handleStop = useCallback(() => {
    setSessionState('stopping');
    audioService.cleanup();
    enkiService.stopAudio();
    enkiService.closeWebSockets();
    setSessionState('idle');
    setStatusMsg('Session stopped');
  }, []);

  const handleToggleMute = useCallback(() => {
    if (muted) {
      enkiService.resumeAudio();
      audioService.startStreaming(sendAudioChunk);
      setMuted(false);
      setStatusMsg('Listening…');
    } else {
      audioService.stopStreaming();
      enkiService.pauseAudio();
      setMuted(true);
      setStatusMsg('Muted');
    }
  }, [muted]);

  const handleDisconnect = useCallback(() => {
    handleStop();
    enkiService.disconnect();
    onDisconnect();
  }, [handleStop, onDisconnect]);

  // ---------------------------------------------------------------------------
  // Render helpers
  // ---------------------------------------------------------------------------

  function _senderColor(sender: string) {
    return sender === 'ADA' ? '#7C6FCD' : '#4caf92';
  }

  // ---------------------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------------------

  const isActive = sessionState === 'active';

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <View>
          <Text style={styles.headerTitle}>Enki AI</Text>
          <Text style={styles.headerSub} numberOfLines={1}>{serverUrl}</Text>
        </View>
        <TouchableOpacity onPress={handleDisconnect} style={styles.disconnectBtn}>
          <Text style={styles.disconnectText}>✕ Disconnect</Text>
        </TouchableOpacity>
      </View>

      {/* Status pill */}
      <View style={[styles.statusPill, isActive && styles.statusPillActive]}>
        <View style={[styles.statusDot, isActive && styles.statusDotActive]} />
        <Text style={styles.statusText}>{statusMsg}</Text>
      </View>

      {/* Transcription feed */}
      <FlatList<TranscriptionMessage>
        ref={flatListRef}
        data={transcripts}
        keyExtractor={(_, i) => String(i)}
        style={styles.transcriptList}
        contentContainerStyle={styles.transcriptContent}
        ListEmptyComponent={
          <Text style={styles.emptyHint}>
            Start a session and speak — your conversation will appear here.
          </Text>
        }
        renderItem={({ item }) => (
          <View style={styles.transcriptRow}>
            <Text style={[styles.sender, { color: _senderColor(item.sender) }]}>
              {item.sender}
            </Text>
            <Text style={styles.transcriptText}>{item.text}</Text>
          </View>
        )}
      />

      {/* Control bar */}
      <View style={styles.controls}>
        {sessionState === 'idle' || sessionState === 'stopping' ? (
          <TouchableOpacity style={styles.primaryBtn} onPress={handleStart} activeOpacity={0.85}>
            <Text style={styles.primaryBtnText}>▶  Start Session</Text>
          </TouchableOpacity>
        ) : sessionState === 'starting' ? (
          <View style={[styles.primaryBtn, styles.primaryBtnDisabled]}>
            <Text style={styles.primaryBtnText}>Starting…</Text>
          </View>
        ) : (
          <View style={styles.activeControls}>
            <TouchableOpacity
              style={[styles.muteBtn, muted && styles.muteBtnActive]}
              onPress={handleToggleMute}
              activeOpacity={0.85}
            >
              <Text style={styles.muteBtnText}>{muted ? '🔇 Unmute' : '🎙 Mute'}</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.stopBtn} onPress={handleStop} activeOpacity={0.85}>
              <Text style={styles.stopBtnText}>⏹ Stop</Text>
            </TouchableOpacity>
          </View>
        )}
      </View>

      {/* Ray-Ban tip */}
      {isActive && (
        <Text style={styles.tip}>
          💡 Tap the Ray-Ban frame to pause / resume (double-tap shortcut)
        </Text>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0a0a0a',
  },

  // Header
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingTop: Platform.OS === 'ios' ? 60 : 24,
    paddingBottom: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#1e1e1e',
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: '#fff',
  },
  headerSub: {
    fontSize: 12,
    color: '#555',
    maxWidth: 200,
  },
  disconnectBtn: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#333',
  },
  disconnectText: {
    color: '#888',
    fontSize: 13,
  },

  // Status
  statusPill: {
    flexDirection: 'row',
    alignItems: 'center',
    alignSelf: 'flex-start',
    backgroundColor: '#1a1a1a',
    borderRadius: 20,
    paddingHorizontal: 14,
    paddingVertical: 8,
    marginHorizontal: 20,
    marginTop: 16,
    gap: 8,
  },
  statusPillActive: {
    backgroundColor: '#1a2a1a',
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#555',
  },
  statusDotActive: {
    backgroundColor: '#4caf50',
  },
  statusText: {
    fontSize: 14,
    color: '#ccc',
  },

  // Transcript
  transcriptList: {
    flex: 1,
    marginTop: 16,
  },
  transcriptContent: {
    paddingHorizontal: 20,
    paddingBottom: 16,
    gap: 12,
  },
  emptyHint: {
    color: '#444',
    textAlign: 'center',
    marginTop: 60,
    fontSize: 14,
    lineHeight: 22,
    paddingHorizontal: 20,
  },
  transcriptRow: {
    backgroundColor: '#141414',
    borderRadius: 10,
    padding: 12,
  },
  sender: {
    fontSize: 11,
    fontWeight: '700',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    marginBottom: 4,
  },
  transcriptText: {
    color: '#ddd',
    fontSize: 15,
    lineHeight: 22,
  },

  // Controls
  controls: {
    paddingHorizontal: 20,
    paddingVertical: 16,
    borderTopWidth: 1,
    borderTopColor: '#1e1e1e',
  },
  primaryBtn: {
    backgroundColor: '#7C6FCD',
    borderRadius: 14,
    paddingVertical: 16,
    alignItems: 'center',
  },
  primaryBtnDisabled: {
    opacity: 0.5,
  },
  primaryBtnText: {
    color: '#fff',
    fontSize: 17,
    fontWeight: '700',
  },
  activeControls: {
    flexDirection: 'row',
    gap: 12,
  },
  muteBtn: {
    flex: 1,
    backgroundColor: '#1e1e1e',
    borderRadius: 14,
    paddingVertical: 14,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#333',
  },
  muteBtnActive: {
    backgroundColor: '#2a2a1e',
    borderColor: '#555',
  },
  muteBtnText: {
    color: '#ccc',
    fontSize: 15,
    fontWeight: '600',
  },
  stopBtn: {
    flex: 1,
    backgroundColor: '#2a1414',
    borderRadius: 14,
    paddingVertical: 14,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#5a1a1a',
  },
  stopBtnText: {
    color: '#ff6b6b',
    fontSize: 15,
    fontWeight: '600',
  },

  // Tip
  tip: {
    textAlign: 'center',
    color: '#444',
    fontSize: 12,
    paddingBottom: 12,
    paddingHorizontal: 20,
  },
});
