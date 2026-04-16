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

const STORAGE_KEY_SERVER = '@enki_server_url';
const DEFAULT_URL = 'http://192.168.1.100:8000';

interface Props {
  onConnected: (serverUrl: string) => void;
}

export default function ConnectScreen({ onConnected }: Props) {
  const [serverUrl, setServerUrl] = useState(DEFAULT_URL);
  const [connecting, setConnecting] = useState(false);

  // Pre-fill last used URL on mount
  React.useEffect(() => {
    AsyncStorage.getItem(STORAGE_KEY_SERVER)
      .then((saved) => { if (saved) setServerUrl(saved); })
      .catch(() => {});
  }, []);

  async function handleConnect() {
    if (!serverUrl.trim()) {
      Alert.alert('Missing URL', 'Please enter your Enki AI server address.');
      return;
    }

    const url = serverUrl.trim().replace(/\/$/, '');
    setConnecting(true);

    // Save for next time
    await AsyncStorage.setItem(STORAGE_KEY_SERVER, url).catch(() => {});

    enkiService.connect(url, {
      onConnectionChange: (status) => {
        if (status === 'connected') {
          setConnecting(false);
          onConnected(url);
        } else if (status === 'disconnected') {
          setConnecting(false);
          Alert.alert('Connection Failed', 'Could not connect to the Enki AI backend. Check the server address and that the backend is running.');
        }
      },
      onError: (msg) => {
        setConnecting(false);
        Alert.alert('Error', msg);
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
          onSubmitEditing={handleConnect}
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

        <Text style={styles.footer}>
          Pair your Ray-Bans with this phone via Bluetooth before connecting.
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
    marginBottom: 40,
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
});
