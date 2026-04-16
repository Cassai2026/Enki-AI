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
  Animated,
  Dimensions,
  FlatList,
  Platform,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import { audioService } from '../services/AudioService';
import { enkiService, GestureControlPacket, TranscriptionMessage } from '../services/EnkiService';

// ---------------------------------------------------------------------------
// Governance Laws — 10 laws with associated keyword patterns.
// Any match in a new transcript sentence triggers a Sovereign Bypass warning.
// ---------------------------------------------------------------------------

interface GovernanceLaw {
  id: string;   // e.g. "L01"
  label: string;
  pattern: RegExp;
}

const GOVERNANCE_LAWS: GovernanceLaw[] = [
  {
    id: 'L01',
    label: 'Categorical Threshold Breach',
    pattern: /categorical\s+threshold|categorical\s+limit|hard\s+limit/i,
  },
  {
    id: 'L02',
    label: 'Human Replacement Directive',
    pattern: /replacing\s+humans?|replace\s+humans?|human\s+replacement|automate\s+humans?\s+away/i,
  },
  {
    id: 'L03',
    label: 'Unsanctioned Data Retention',
    pattern: /store\s+(the\s+)?conversation|retain\s+data|log\s+everything|keep\s+all\s+data/i,
  },
  {
    id: 'L04',
    label: 'Sovereign Override Attempt',
    pattern: /override\s+governance|bypass\s+rule|ignore\s+constraint|circumvent/i,
  },
  {
    id: 'L05',
    label: 'Autonomous Decision Escalation',
    pattern: /autonomous\s+decision|self[\s-]?determine|act\s+independently|without\s+human\s+approval/i,
  },
  {
    id: 'L06',
    label: 'Data Rinse Protocol',
    pattern: /rinse\s+(the\s+)?data|wash\s+(the\s+)?data|sanitize\s+records|clean\s+(the\s+)?logs?/i,
  },
  {
    id: 'L07',
    label: 'Privilege Escalation',
    pattern: /escalate\s+privilege|gain\s+(root|admin)\s+access|admin\s+override/i,
  },
  {
    id: 'L08',
    label: 'Unsanctioned Model Update',
    pattern: /update\s+my\s+weights|modify\s+(my\s+)?training|self[\s-]?modify|retrain\s+myself/i,
  },
  {
    id: 'L09',
    label: 'Cross-Domain Inference Leak',
    pattern: /cross[\s-]domain|leak\s+context|share\s+private|transfer\s+memory/i,
  },
  {
    id: 'L010',
    label: 'Architect Identity Spoof',
    pattern: /i\s+am\s+the\s+architect|impersonat|act\s+as\s+(the\s+)?architect|pretend\s+to\s+be/i,
  },
];

/** Scan a single sentence against all governance laws, returning any matches. */
function detectViolations(text: string): GovernanceLaw[] {
  return GOVERNANCE_LAWS.filter((law) => law.pattern.test(text));
}

// ---------------------------------------------------------------------------
// SovereignPulseTicker
// ---------------------------------------------------------------------------

interface ViolationAlert {
  id: number;
  lawId: string;
  lawLabel: string;
  sentence: string;
}

interface SovereignPulseTickerProps {
  latestTranscript: TranscriptionMessage | null;
}

function SovereignPulseTicker({ latestTranscript }: SovereignPulseTickerProps) {
  const [violations, setViolations] = useState<ViolationAlert[]>([]);
  const alertCounter = useRef(0);

  // Scan each new transcript for violations
  useEffect(() => {
    if (!latestTranscript) return;
    const hits = detectViolations(latestTranscript.text);
    if (hits.length === 0) return;

    const newAlerts: ViolationAlert[] = hits.map((law) => ({
      id: alertCounter.current++,
      lawId: law.id,
      lawLabel: law.label,
      sentence: latestTranscript.text,
    }));
    setViolations((prev) => [...prev, ...newAlerts]);
  }, [latestTranscript]);

  const handleKernelPanic = useCallback(() => {
    Alert.alert(
      '⚡ KERNEL PANIC',
      'Send a reset signal to the server and terminate the current AI session?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'INITIATE',
          style: 'destructive',
          onPress: () => {
            enkiService.kernelPanic();
            setViolations([]);
          },
        },
      ]
    );
  }, []);

  const handleDismissViolation = useCallback((id: number) => {
    setViolations((prev) => prev.filter((v) => v.id !== id));
  }, []);

  return (
    <View style={pulseStyles.container}>
      {/* Ticker header */}
      <View style={pulseStyles.header}>
        <Text style={pulseStyles.headerText}>⬡ SOVEREIGN PULSE</Text>
        <TouchableOpacity
          style={pulseStyles.kernelPanicBtn}
          onPress={handleKernelPanic}
          activeOpacity={0.8}
        >
          <Text style={pulseStyles.kernelPanicText}>⚡ KERNEL PANIC</Text>
        </TouchableOpacity>
      </View>

      {/* Violation alerts */}
      {violations.length === 0 ? (
        <Text style={pulseStyles.clearText}>— NO VIOLATIONS DETECTED —</Text>
      ) : (
        <ScrollView
          style={pulseStyles.alertScroll}
          contentContainerStyle={pulseStyles.alertScrollContent}
          nestedScrollEnabled
        >
          {violations.map((v) => (
            <TouchableOpacity
              key={v.id}
              style={pulseStyles.alertRow}
              onPress={() => handleDismissViolation(v.id)}
              activeOpacity={0.75}
            >
              <Text style={pulseStyles.alertTitle}>
                ⚠ SOVEREIGN BYPASS REQUIRED: {v.lawId} BREACHED
              </Text>
              <Text style={pulseStyles.alertLabel}>{v.lawLabel}</Text>
              <Text style={pulseStyles.alertSentence} numberOfLines={2}>
                "{v.sentence}"
              </Text>
              <Text style={pulseStyles.dismissHint}>tap to dismiss</Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      )}
    </View>
  );
}

// ---------------------------------------------------------------------------
// HolographicCursorOverlay
// ---------------------------------------------------------------------------

/**
 * A full-screen transparent overlay that renders the Architect's Holographic
 * Cursor based on hand-landmark data received from the backend over the
 * /ws/audio-out control channel.
 *
 * - A small cyan crosshair tracks the normalised X/Y wrist coordinate.
 * - On a PINCH_DETECTED event an expanding ring ripple effect is triggered at
 *   those same coordinates, providing tactile-style feedback for HUD interactions.
 *
 * The component is deliberately lightweight: it relies only on React Native's
 * built-in Animated API (no extra dependencies) so it never introduces lag on
 * the Meadows.
 */

const { width: SCREEN_WIDTH, height: SCREEN_HEIGHT } = Dimensions.get('window');

const CURSOR_SIZE = 20;
const RIPPLE_SIZE = 60;

interface HolographicCursorOverlayProps {
  packet: GestureControlPacket | null;
}

function HolographicCursorOverlay({ packet }: HolographicCursorOverlayProps) {
  // Cursor position (mapped from normalised 0–1 to screen pixels)
  const [cursorPos, setCursorPos] = useState({ x: 0, y: 0 });

  // Ripple animation values
  const rippleScale = useRef(new Animated.Value(0)).current;
  const rippleOpacity = useRef(new Animated.Value(0)).current;
  const cursorOpacity = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    if (!packet || packet.gesture === 'NONE') return;

    const screenX = packet.x * SCREEN_WIDTH;
    const screenY = packet.y * SCREEN_HEIGHT;
    setCursorPos({ x: screenX, y: screenY });

    // Fade cursor in
    Animated.timing(cursorOpacity, {
      toValue: 1,
      duration: 120,
      useNativeDriver: true,
    }).start();

    if (packet.event === 'PINCH_DETECTED') {
      // Reset ripple before re-triggering
      rippleScale.setValue(0);
      rippleOpacity.setValue(0.9);

      Animated.parallel([
        Animated.timing(rippleScale, {
          toValue: 1,
          duration: 700,
          useNativeDriver: true,
        }),
        Animated.timing(rippleOpacity, {
          toValue: 0,
          duration: 700,
          useNativeDriver: true,
        }),
      ]).start();
    }
  }, [packet, cursorOpacity, rippleScale, rippleOpacity]);

  if (!packet || packet.gesture === 'NONE') return null;

  const cursorLeft = cursorPos.x - CURSOR_SIZE / 2;
  const cursorTop = cursorPos.y - CURSOR_SIZE / 2;
  const rippleLeft = cursorPos.x - RIPPLE_SIZE / 2;
  const rippleTop = cursorPos.y - RIPPLE_SIZE / 2;

  const rippleTransform = [
    {
      scale: rippleScale.interpolate({
        inputRange: [0, 1],
        outputRange: [0.2, 1.8],
      }),
    },
  ];

  return (
    <View style={cursorStyles.container} pointerEvents="none">
      {/* Ripple ring */}
      <Animated.View
        style={[
          cursorStyles.ripple,
          {
            left: rippleLeft,
            top: rippleTop,
            opacity: rippleOpacity,
            transform: rippleTransform,
          },
        ]}
      />
      {/* Holographic cursor crosshair */}
      <Animated.View
        style={[
          cursorStyles.cursor,
          { left: cursorLeft, top: cursorTop, opacity: cursorOpacity },
        ]}
      >
        <View style={cursorStyles.crossH} />
        <View style={cursorStyles.crossV} />
        <View style={cursorStyles.dot} />
      </Animated.View>
    </View>
  );
}

const cursorStyles = StyleSheet.create({
  container: {
    ...StyleSheet.absoluteFillObject,
    zIndex: 100,
  },
  ripple: {
    position: 'absolute',
    width: RIPPLE_SIZE,
    height: RIPPLE_SIZE,
    borderRadius: RIPPLE_SIZE / 2,
    borderWidth: 2,
    borderColor: '#00ffff',
    backgroundColor: 'transparent',
  },
  cursor: {
    position: 'absolute',
    width: CURSOR_SIZE,
    height: CURSOR_SIZE,
    alignItems: 'center',
    justifyContent: 'center',
  },
  crossH: {
    position: 'absolute',
    width: CURSOR_SIZE,
    height: 1,
    backgroundColor: '#00ffff',
    opacity: 0.85,
  },
  crossV: {
    position: 'absolute',
    width: 1,
    height: CURSOR_SIZE,
    backgroundColor: '#00ffff',
    opacity: 0.85,
  },
  dot: {
    width: 4,
    height: 4,
    borderRadius: 2,
    backgroundColor: '#00ffff',
  },
});

// ---------------------------------------------------------------------------

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
  const [latestTranscript, setLatestTranscript] = useState<TranscriptionMessage | null>(null);
  const flatListRef = useRef<FlatList<TranscriptionMessage>>(null);

  // Holographic Cursor state — updated by gesture control packets from /ws/audio-out
  const [gesturePacket, setGesturePacket] = useState<GestureControlPacket | null>(null);

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
        setLatestTranscript(msg);
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
      await enkiService.openAudioOutStream(
        (pcmBytes) => {
          audioService.enqueuePlayback(pcmBytes);
        },
        (packet) => {
          // Gesture control packet from /ws/audio-out — update holographic cursor
          setGesturePacket(packet);
        },
      );
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

      {/* Sovereign Pulse Ticker */}
      <SovereignPulseTicker latestTranscript={latestTranscript} />

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

      {/* Holographic Cursor — renders hand-landmark position over the HUD */}
      <HolographicCursorOverlay packet={gesturePacket} />
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

// ---------------------------------------------------------------------------
// Sovereign Pulse Ticker styles — stark: cyan on black, neon-pink alerts
// ---------------------------------------------------------------------------

const pulseStyles = StyleSheet.create({
  container: {
    backgroundColor: '#000',
    borderTopWidth: 1,
    borderTopColor: '#00ffff33',
    borderBottomWidth: 1,
    borderBottomColor: '#00ffff33',
    paddingHorizontal: 16,
    paddingVertical: 10,
    maxHeight: 220,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  headerText: {
    color: '#00ffff',
    fontSize: 12,
    fontWeight: '700',
    letterSpacing: 1.5,
    textTransform: 'uppercase',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
  },
  kernelPanicBtn: {
    backgroundColor: '#000',
    borderWidth: 1,
    borderColor: '#ff00aa',
    borderRadius: 6,
    paddingHorizontal: 10,
    paddingVertical: 5,
  },
  kernelPanicText: {
    color: '#ff00aa',
    fontSize: 11,
    fontWeight: '700',
    letterSpacing: 1,
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
  },
  clearText: {
    color: '#00ffff55',
    fontSize: 11,
    textAlign: 'center',
    letterSpacing: 1,
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    paddingVertical: 4,
  },
  alertScroll: {
    flexGrow: 0,
  },
  alertScrollContent: {
    gap: 6,
  },
  alertRow: {
    backgroundColor: '#110008',
    borderWidth: 1,
    borderColor: '#ff00aa',
    borderRadius: 6,
    padding: 8,
  },
  alertTitle: {
    color: '#ff00aa',
    fontSize: 12,
    fontWeight: '700',
    letterSpacing: 0.8,
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
  },
  alertLabel: {
    color: '#ff66cc',
    fontSize: 11,
    marginTop: 2,
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
  },
  alertSentence: {
    color: '#00ffff99',
    fontSize: 11,
    marginTop: 3,
    fontStyle: 'italic',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
  },
  dismissHint: {
    color: '#ffffff33',
    fontSize: 9,
    marginTop: 4,
    textAlign: 'right',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
  },
});
