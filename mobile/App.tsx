import React, { useState } from 'react';
import { StatusBar } from 'expo-status-bar';
import { StyleSheet, View } from 'react-native';
import ConnectScreen from './src/screens/ConnectScreen';
import ActiveScreen from './src/screens/ActiveScreen';

export type AppScreen = 'connect' | 'active';

export default function App() {
  const [screen, setScreen] = useState<AppScreen>('connect');
  const [serverUrl, setServerUrl] = useState<string>('');

  function handleConnected(url: string) {
    setServerUrl(url);
    setScreen('active');
  }

  function handleDisconnected() {
    setScreen('connect');
    setServerUrl('');
  }

  return (
    <View style={styles.container}>
      <StatusBar style="light" />
      {screen === 'connect' ? (
        <ConnectScreen onConnected={handleConnected} />
      ) : (
        <ActiveScreen serverUrl={serverUrl} onDisconnect={handleDisconnected} />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0a0a0a',
  },
});
