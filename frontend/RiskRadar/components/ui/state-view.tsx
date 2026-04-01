import React from 'react';
import {
  View,
  Text,
  ActivityIndicator,
  TouchableOpacity,
  StyleSheet,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Colors } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';

interface StateViewProps {
  state: 'loading' | 'empty' | 'error' | 'success';
  loadingText?: string;
  emptyText?: string;
  emptyIcon?: string;
  errorText?: string;
  onRetry?: () => void;
  children?: React.ReactNode;
}

export function StateView({
  state,
  loadingText = 'Loading...',
  emptyText = 'No data available',
  emptyIcon = 'document-outline',
  errorText = 'Something went wrong',
  onRetry,
  children,
}: StateViewProps) {
  const scheme = useColorScheme() ?? 'light';
  const palette = Colors[scheme];
  const styles = getStyles(palette);

  if (state === 'loading') {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color={palette.primary} />
        <Text style={[styles.text, { color: palette.textSecondary }]}>
          {loadingText}
        </Text>
      </View>
    );
  }

  if (state === 'empty') {
    return (
      <View style={styles.container}>
        <Ionicons name={emptyIcon as any} size={48} color={palette.textSecondary} />
        <Text style={[styles.text, { color: palette.textSecondary }]}>
          {emptyText}
        </Text>
      </View>
    );
  }

  if (state === 'error') {
    return (
      <View style={styles.container}>
        <Ionicons name="alert-circle-outline" size={48} color={palette.danger} />
        <Text style={[styles.text, { color: palette.danger }]}>
          {errorText}
        </Text>
        {onRetry && (
          <TouchableOpacity style={styles.retryButton} onPress={onRetry}>
            <Text style={[styles.retryText, { color: palette.primary }]}>
              Try Again
            </Text>
          </TouchableOpacity>
        )}
      </View>
    );
  }

  // Success state
  return <>{children}</>;
}

function getStyles(palette: typeof Colors.light) {
  return StyleSheet.create({
    container: {
      flex: 1,
      justifyContent: 'center',
      alignItems: 'center',
      padding: 20,
    },
    text: {
      fontSize: 16,
      textAlign: 'center',
      marginTop: 12,
    },
    retryButton: {
      marginTop: 16,
      paddingHorizontal: 20,
      paddingVertical: 10,
      borderRadius: 8,
      borderWidth: 1,
      borderColor: palette.primary,
    },
    retryText: {
      fontSize: 16,
      fontWeight: '600',
    },
  });
}