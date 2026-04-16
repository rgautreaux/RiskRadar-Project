import { DefaultTheme, ThemeProvider, type Theme } from '@react-navigation/native';
import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { ActivityIndicator, View } from 'react-native';
import 'react-native-reanimated';

import { Colors } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { AuthProvider, useAuth } from '@/contexts/auth-context';

export const unstable_settings = {
  anchor: '(tabs)',
};

export default function RootLayout() {
  return (
    <AuthProvider>
      <RootNavigator />
    </AuthProvider>
  );
}

function RootNavigator() {
  const scheme = useColorScheme() ?? 'light';
  const palette = Colors[scheme];
  const { isLoading } = useAuth();

  const navigationTheme: Theme = {
    ...DefaultTheme,
    dark: false,
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

  if (isLoading) {
    return (
      <ThemeProvider value={navigationTheme}>
        <View
          style={{
            flex: 1,
            justifyContent: 'center',
            alignItems: 'center',
            backgroundColor: palette.background,
          }}
        >
          <ActivityIndicator size="large" color={palette.primary} />
        </View>
        <StatusBar style="dark" backgroundColor={palette.primaryDark} />
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider value={navigationTheme}>
      <Stack
        screenOptions={{
          contentStyle: { backgroundColor: palette.background },
          headerStyle: { backgroundColor: palette.primaryDark },
          headerTintColor: palette.white,
          headerShadowVisible: false,
        }}>
        <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
        <Stack.Screen name="welcome" options={{ headerShown: false }} />
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
      <StatusBar style="dark" backgroundColor={palette.primaryDark} />
    </ThemeProvider>
  );
}
