import { useCallback, useEffect, useState } from 'react';
import { StatusBar } from 'expo-status-bar';
import { StyleSheet, View } from 'react-native';

import { CameraScreen } from './src/screens/CameraScreen';
import { ConsentScreen } from './src/screens/ConsentScreen';
import { HomeScreen } from './src/screens/HomeScreen';
import { ProcessingScreen } from './src/screens/ProcessingScreen';
import { ResultScreen } from './src/screens/ResultScreen';
import { SceneSelectionScreen } from './src/screens/SceneSelectionScreen';
import { colors } from './src/theme';
import type { AppStep, Scene } from './src/types';

const SESSION_TIMEOUT_MS = 60_000;

export default function App() {
  const [step, setStep] = useState<AppStep>('home');
  const [scene, setScene] = useState<Scene | null>(null);
  const [photoUri, setPhotoUri] = useState<string | null>(null);
  const [sessionVersion, setSessionVersion] = useState(0);

  const resetSession = useCallback(() => {
    setStep('home');
    setScene(null);
    setPhotoUri(null);
    setSessionVersion((value) => value + 1);
  }, []);

  useEffect(() => {
    if (step === 'home' || step === 'camera' || step === 'processing') return;
    const timeout = setTimeout(resetSession, SESSION_TIMEOUT_MS);
    return () => clearTimeout(timeout);
  }, [resetSession, sessionVersion, step]);

  const selectScene = (selectedScene: Scene) => {
    setScene(selectedScene);
    setStep('consent');
    setSessionVersion((value) => value + 1);
  };

  return (
    <View style={styles.app}>
      <StatusBar style="light" hidden />
      {step === 'home' && <HomeScreen onStart={() => setStep('scenes')} />}
      {step === 'scenes' && (
        <SceneSelectionScreen onBack={() => setStep('home')} onSelect={selectScene} />
      )}
      {step === 'consent' && scene && (
        <ConsentScreen
          scene={scene}
          onAccept={() => setStep('camera')}
          onBack={() => setStep('scenes')}
        />
      )}
      {step === 'camera' && scene && (
        <CameraScreen
          scene={scene}
          onBack={() => setStep('consent')}
          onCapture={(uri) => {
            setPhotoUri(uri);
            setStep('processing');
          }}
        />
      )}
      {step === 'processing' && scene && photoUri && (
        <ProcessingScreen scene={scene} onComplete={() => setStep('result')} />
      )}
      {step === 'result' && scene && photoUri && (
        <ResultScreen
          scene={scene}
          capturedPhotoUri={photoUri}
          onRetake={() => setStep('camera')}
          onRestart={resetSession}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  app: {
    flex: 1,
    backgroundColor: colors.background,
  },
});
