import React, { useRef, useCallback } from 'react';
import { Animated, Text, StyleSheet, ViewStyle, TextStyle, GestureResponderEvent, Pressable } from 'react-native';
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
  const scale = useRef(new Animated.Value(1)).current;

  const handlePressIn = useCallback(() => {
    Animated.timing(scale, {
      toValue: 0.96,
      duration: 100,
      useNativeDriver: true,
    }).start();
  }, []);

  const handlePressOut = useCallback(() => {
    Animated.timing(scale, {
      toValue: 1,
      duration: 150,
      useNativeDriver: true,
    }).start();
  }, []);

  return (
    <Pressable
      onPress={onPress}
      onPressIn={handlePressIn}
      onPressOut={handlePressOut}
      disabled={disabled || loading}
    >
      <Animated.View
        style={[
          styles.button,
          { backgroundColor: disabled ? palette.textSecondary : palette.primary, shadowColor: palette.primary },
          style,
          { transform: [{ scale }] },
        ]}
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
      </Animated.View>
    </Pressable>
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
