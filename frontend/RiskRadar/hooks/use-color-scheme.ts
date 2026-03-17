import { useColorScheme as _useColorScheme } from 'react-native';

/**
 * Returns the user's current color scheme preference ('light' or 'dark').
 * Wraps React Native's useColorScheme to provide a stable, typed interface.
 */
export function useColorScheme(): 'light' | 'dark' {
  return _useColorScheme() ?? 'light';
}
