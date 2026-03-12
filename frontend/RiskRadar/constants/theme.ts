import { Platform } from 'react-native';

const fontFamilies =
  Platform.select({
    ios: {
      sans: 'system-ui',
      serif: 'ui-serif',
      rounded: 'ui-rounded',
      mono: 'ui-monospace',
    },
    default: {
      sans: 'normal',
      serif: 'serif',
      rounded: 'normal',
      mono: 'monospace',
    },
    web: {
      sans: "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
      serif: "Georgia, 'Times New Roman', serif",
      rounded: "'Trebuchet MS', 'Avenir Next', 'Segoe UI', sans-serif",
      mono: "SFMono-Regular, Menlo, Monaco, Consolas, 'Courier New', monospace",
    },
  }) ?? {
    sans: 'normal',
    serif: 'serif',
    rounded: 'normal',
    mono: 'monospace',
  };

export const BrandPalette = {
  primary: '#0B5FA5',
  primaryDark: '#083B73',
  secondary: '#D9ECFB',
  warning: '#F59E0B',
  danger: '#D64545',
  surface: '#F6FAFD',
  surfaceMuted: '#EAF2F8',
  border: '#C7D8E6',
  textPrimary: '#16324A',
  textSecondary: '#5B748A',
  success: '#2E8B57',
  white: '#FFFFFF',
  shadow: 'rgba(8, 59, 115, 0.14)',
} as const;

const lightColors = {
  text: BrandPalette.textPrimary,
  textSecondary: BrandPalette.textSecondary,
  background: BrandPalette.surface,
  tint: BrandPalette.primary,
  icon: BrandPalette.primaryDark,
  tabIconDefault: BrandPalette.textSecondary,
  tabIconSelected: BrandPalette.primary,
  surface: BrandPalette.surface,
  surfaceMuted: BrandPalette.surfaceMuted,
  border: BrandPalette.border,
  danger: BrandPalette.danger,
  warning: BrandPalette.warning,
  success: BrandPalette.success,
  shadow: BrandPalette.shadow,
  card: BrandPalette.white,
  link: BrandPalette.primary,
  primary: BrandPalette.primary,
  primaryDark: BrandPalette.primaryDark,
  secondary: BrandPalette.secondary,
  white: BrandPalette.white,
};

export const Colors = {
  light: lightColors,
  dark: lightColors,
};

export const Fonts = fontFamilies;

export const Spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 40,
} as const;

export const Radius = {
  sm: 10,
  md: 16,
  lg: 24,
  pill: 999,
  button: 18,
} as const;

export const Typography = {
  hero: {
    fontFamily: Fonts.rounded,
    fontSize: 32,
    lineHeight: 36,
    fontWeight: '700',
  },
  title: {
    fontFamily: Fonts.sans,
    fontSize: 26,
    lineHeight: 30,
    fontWeight: '700',
  },
  subtitle: {
    fontFamily: Fonts.sans,
    fontSize: 18,
    lineHeight: 22,
    fontWeight: '600',
  },
  sectionLabel: {
    fontFamily: Fonts.rounded,
    fontSize: 20,
    lineHeight: 24,
    fontWeight: '600',
  },
  cardHeading: {
    fontFamily: Fonts.sans,
    fontSize: 16,
    lineHeight: 20,
    fontWeight: '600',
  },
  body: {
    fontFamily: Fonts.sans,
    fontSize: 15,
    lineHeight: 22,
    fontWeight: '400',
  },
  meta: {
    fontFamily: Fonts.sans,
    fontSize: 12,
    lineHeight: 16,
    fontWeight: '500',
  },
} as const;

export const Shadows = {
  card: {
    shadowColor: BrandPalette.primaryDark,
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.14,
    shadowRadius: 24,
    elevation: 4,
  },
} as const;
