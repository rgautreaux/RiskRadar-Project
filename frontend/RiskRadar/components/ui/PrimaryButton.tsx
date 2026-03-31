import React from 'react';
import { TouchableOpacity, Text, StyleSheet, ViewStyle, TextStyle, GestureResponderEvent } from 'react-native';
import { Colors, Spacing, Radius, Fonts } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';

export interface PrimaryButtonProps {
  label: string;
  onPress: (event: GestureResponderEvent) => void;
  style?: ViewStyle;
  textStyle?: TextStyle;
  disabled?: boolean;
  loading?: boolean;
  leftIcon?: React.ReactNode;
}

export function PrimaryButton({
  label,
  onPress,
  style,
  textStyle,
  disabled = false,
  loading = false,
  leftIcon,
}: PrimaryButtonProps) {
  const scheme = useColorScheme() ?? 'light';
  const palette = Colors[scheme];

  return (
    <TouchableOpacity
      style={[
        styles.button,
        { backgroundColor: disabled ? palette.textSecondary : palette.primary, shadowColor: palette.primary },
        style,
      ]}
      onPress={onPress}
      activeOpacity={0.8}
      disabled={disabled || loading}
    >
      {leftIcon && <>{leftIcon}</>}
      <Text
        style={[
          styles.label,
          { color: palette.white, fontFamily: Fonts.sans },
          textStyle,
        ]}
      >
        {loading ? '...' : label}
      </Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  button: {
    flexDirection: 'row',
    width: '100%',
    height: 56,
    borderRadius: Radius.button,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: Spacing.md,
    paddingHorizontal: Spacing.lg,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 4.65,
    elevation: 8,
  },
  label: {
    fontSize: 16,
    fontWeight: '700',
    letterSpacing: 0.5,
  },
});

export default PrimaryButton;
