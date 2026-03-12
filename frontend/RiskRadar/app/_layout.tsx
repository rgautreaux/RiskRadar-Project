import { DefaultTheme, ThemeProvider, type Theme } from '@react-navigation/native';
import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import 'react-native-reanimated';

import { Colors } from '@/constants/theme';

export const unstable_settings = {
  anchor: '(tabs)',
};

const navigationTheme: Theme = {
  ...DefaultTheme,
  dark: false,
  colors: {
    ...DefaultTheme.colors,
    primary: Colors.light.primary,
    background: Colors.light.background,
    card: Colors.light.primaryDark,
    text: Colors.light.text,
    border: Colors.light.border,
    notification: Colors.light.danger,
  },
};

export default function RootLayout() {
  return (
    <ThemeProvider value={navigationTheme}>
      <Stack
        screenOptions={{
          contentStyle: { backgroundColor: Colors.light.background },
          headerStyle: { backgroundColor: Colors.light.primaryDark },
          headerTintColor: Colors.light.white,
          headerShadowVisible: false,
        }}>
        <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
        <Stack.Screen
          name="modal"
          options={{
            presentation: 'modal',
            title: 'Notifications',
          }}
        />
      </Stack>
      <StatusBar style="light" backgroundColor={Colors.light.primaryDark} />
    </ThemeProvider>
  );
}
