import { DefaultTheme, ThemeProvider, type Theme } from '@react-navigation/native';
import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import 'react-native-reanimated';

import { Colors } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { AuthProvider } from '@/contexts/auth-context';

export const unstable_settings = {
  anchor: '(tabs)',
};

export default function RootLayout() {
  const scheme = useColorScheme() ?? 'light';
  const palette = Colors[scheme];

  const navigationTheme: Theme = {
    ...DefaultTheme,
    dark: scheme === 'dark',
    colors: {
      ...DefaultTheme.colors,
      primary: palette.primary,
      background: palette.background,
      card: palette.primaryDark,
      text: palette.text,
      border: palette.border,
      notification: palette.danger,
    },
  };

  return (
    <AuthProvider>
      <ThemeProvider value={navigationTheme}>
        <Stack
          screenOptions={{
            contentStyle: { backgroundColor: palette.background },
            headerStyle: { backgroundColor: palette.primaryDark },
            headerTintColor: palette.white,
            headerShadowVisible: false,
          }}>
          <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
          <Stack.Screen name="auth" options={{ headerShown: false }} />
          <Stack.Screen name="main" options={{ headerShown: false }} />
          <Stack.Screen
            name="modal"
            options={{
              presentation: 'modal',
              title: 'Notifications',
            }}
          />
        </Stack>
        <StatusBar style={scheme === 'dark' ? 'light' : 'dark'} backgroundColor={palette.primaryDark} />
      </ThemeProvider>
    </AuthProvider>
  );
}
