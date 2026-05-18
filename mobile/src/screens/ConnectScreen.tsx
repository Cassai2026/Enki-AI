import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  Alert,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { enkiService } from '../services/EnkiService';
import { appConfig, sanitizeServerUrl } from '../config/appConfig';
import { telemetryService } from '../services/TelemetryService';

const STORAGE_KEY_SERVER = '@enki_server_url';

interface Props {
  onConnected: (serverUrl: string) => void;
}

export default function ConnectScreen({ onConnected }: Props) {
  const [serverUrl, setServerUrl] = useState(appConfig.defaultBackendUrl);
  const [connecting, setConnecting] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string>('');

  // Pre-fill last used URL on mount
  React.useEffect(() => {
    AsyncStorage.getItem(STORAGE_KEY_SERVER)
      .then((saved) => {
        if (saved) setServerUrl(saved);
      })
      .catch(() => {});
  }, []);

  async function handleConnect(targetUrl?: string) {
    if (connecting) return;

    const input = targetUrl ?? serverUrl;
    if (!input.trim()) {
      Alert.alert('Missing URL', 'Please enter your Enki AI server address.');
      return;
    }

    const url = sanitizeServerUrl(input);
    if (!url) {
      Alert.alert(
        'Invalid URL',
        'Enter a valid backend URL, for example http://192.168.1.100:8000'
      );
      return;
    }

    setConnecting(true);
    setErrorMsg('');
    setServerUrl(url);

    // Save for next time
    await AsyncStorage.setItem(STORAGE_KEY_SERVER, url).catch(() => {});
    enkiService.setSovereignToken(appConfig.sovereignToken);
    void telemetryService.info('connect_attempt', 'Attempting backend connection', {
      environment: appConfig.environment,
      url,
    });

    enkiService.connect(url, {
      onConnectionChange: (status) => {
        if (status === 'connected') {
          setConnecting(false);
          setErrorMsg('');
          void telemetryService.info('connect_success', 'Backend connection established', { url });
          onConnected(url);
        } else if (status === 'disconnected') {
          setConnecting(false);
          const msg =
            'Could not connect to the Enki AI backend. Confirm your phone and server are on the same Wi‑Fi, URL is correct, and backend is running.';
          setErrorMsg(msg);
          void telemetryService.warn('connect_disconnected', msg, { url });
        }
      },
      onError: (msg) => {
        setConnecting(false);
        setErrorMsg(msg);
        void telemetryService.error('connect_error', msg, { url });
      },
    });
  }

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={styles.container}
    >
      <View style={styles.inner}>
        {/* Logo / Title */}
        <Text style={styles.logo}>⬡</Text>
        <Text style={styles.title}>Enki AI</Text>
        <Text style={styles.subtitle}>Meta Ray-Ban Companion</Text>
        <Text style={styles.environmentBadge}>
          {appConfig.environment.toUpperCase()} • iOS + Android
        </Text>

        {/* Server URL input */}
        <Text style={styles.label}>Backend Server URL</Text>
        <TextInput
          style={styles.input}
          value={serverUrl}
          onChangeText={setServerUrl}
          placeholder="http://192.168.1.100:8000"
          placeholderTextColor="#555"
          autoCapitalize="none"
          autoCorrect={false}
          keyboardType="url"
          onSubmitEditing={() => handleConnect()}
          returnKeyType="go"
        />

        <Text style={styles.hint}>
          Make sure your phone and the Enki AI server are on the{' '}
          <Text style={styles.hintBold}>same Wi-Fi network</Text>.
          {'\n'}Run <Text style={styles.code}>python backend/server.py</Text> on your desktop.
        </Text>

        <TouchableOpacity
          style={[styles.button, connecting && styles.buttonDisabled]}
          onPress={handleConnect}
          disabled={connecting}
          activeOpacity={0.8}
        >
          {connecting ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.buttonText}>Connect</Text>
          )}
        </TouchableOpacity>

        {!!errorMsg && (
          <View style={styles.errorCard}>
            <Text style={styles.errorTitle}>Connection failed</Text>
            <Text style={styles.errorText}>{errorMsg}</Text>
            <TouchableOpacity
              style={styles.retryButton}
              onPress={() => handleConnect(serverUrl)}
              activeOpacity={0.85}
            >
              <Text style={styles.retryButtonText}>Retry</Text>
            </TouchableOpacity>
          </View>
        )}

        <Text style={styles.footer}>
          Pair your Ray-Bans with this phone via Bluetooth before connecting.
        </Text>
        <Text style={styles.disclosure}>
          By connecting, voice/audio streams are sent to your configured Enki server. If enabled by
          your deployment, camera frames can also be forwarded for vision responses.
        </Text>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0a0a0a',
  },
  inner: {
    flex: 1,
    justifyContent: 'center',
    paddingHorizontal: 28,
    paddingBottom: 32,
  },
  logo: {
    fontSize: 56,
    textAlign: 'center',
    color: '#7C6FCD',
    marginBottom: 8,
  },
  title: {
    fontSize: 32,
    fontWeight: '700',
    color: '#ffffff',
    textAlign: 'center',
    letterSpacing: 1,
  },
  subtitle: {
    fontSize: 15,
    color: '#888',
    textAlign: 'center',
    marginBottom: 10,
  },
  environmentBadge: {
    alignSelf: 'center',
    marginBottom: 26,
    backgroundColor: '#121212',
    color: '#8f8f8f',
    borderWidth: 1,
    borderColor: '#2f2f2f',
    borderRadius: 14,
    paddingHorizontal: 10,
    paddingVertical: 4,
    fontSize: 11,
    letterSpacing: 0.6,
    fontWeight: '600',
  },
  label: {
    fontSize: 13,
    color: '#aaa',
    marginBottom: 8,
    fontWeight: '600',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  input: {
    backgroundColor: '#1a1a1a',
    color: '#fff',
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 14,
    fontSize: 16,
    borderWidth: 1,
    borderColor: '#333',
    marginBottom: 16,
  },
  hint: {
    fontSize: 13,
    color: '#666',
    lineHeight: 20,
    marginBottom: 28,
  },
  hintBold: {
    color: '#999',
    fontWeight: '600',
  },
  code: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    color: '#7C6FCD',
  },
  button: {
    backgroundColor: '#7C6FCD',
    borderRadius: 14,
    paddingVertical: 16,
    alignItems: 'center',
    marginBottom: 20,
  },
  buttonDisabled: {
    opacity: 0.5,
  },
  buttonText: {
    color: '#fff',
    fontSize: 17,
    fontWeight: '700',
    letterSpacing: 0.3,
  },
  footer: {
    fontSize: 12,
    color: '#444',
    textAlign: 'center',
    lineHeight: 18,
  },
  errorCard: {
    marginBottom: 18,
    padding: 12,
    borderRadius: 12,
    backgroundColor: '#2a1414',
    borderWidth: 1,
    borderColor: '#5a1a1a',
  },
  errorTitle: {
    color: '#ff7d7d',
    fontSize: 13,
    fontWeight: '700',
    marginBottom: 4,
  },
  errorText: {
    color: '#d7b4b4',
    fontSize: 12,
    lineHeight: 17,
  },
  retryButton: {
    marginTop: 10,
    alignSelf: 'flex-start',
    backgroundColor: '#3a1a1a',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 7,
    borderWidth: 1,
    borderColor: '#6a2b2b',
  },
  retryButtonText: {
    color: '#ffc7c7',
    fontSize: 12,
    fontWeight: '700',
  },
  disclosure: {
    marginTop: 14,
    fontSize: 11,
    color: '#505050',
    textAlign: 'center',
    lineHeight: 16,
  },
});
