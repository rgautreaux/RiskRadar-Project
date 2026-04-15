import React, { useEffect, useRef } from 'react';
import {
  StyleSheet,
  TouchableOpacity,
  SafeAreaView,
  View,
  Animated,
  ViewStyle,
} from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { PrimaryButton } from '@/components/ui/PrimaryButton';

import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { Colors, Spacing } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { useAuth } from '@/contexts/auth-context';

/** Reusable fade-in + slide-up wrapper */
function FadeInView({ delay = 0, children, style }: { delay?: number; children: React.ReactNode; style?: ViewStyle }) {
  const opacity = useRef(new Animated.Value(0)).current;
  const translateY = useRef(new Animated.Value(18)).current;
  useEffect(() => {
    const timer = setTimeout(() => {
      Animated.parallel([
        Animated.timing(opacity, { toValue: 1, duration: 450, useNativeDriver: true }),
        Animated.timing(translateY, { toValue: 0, duration: 450, useNativeDriver: true }),
      ]).start();
    }, delay);
    return () => clearTimeout(timer);
  }, []);
  return <Animated.View style={[style, { opacity, transform: [{ translateY }] }]}>{children}</Animated.View>;
}

export default function WelcomeScreen() {
  const router = useRouter();
  const scheme = useColorScheme() ?? 'light';
  const palette = Colors[scheme];
  const { enterGuestMode } = useAuth();

  const handleLogin = () => {
    router.push('/auth/login');
  };

  const handleCreateAccount = () => {
    router.push('/auth/registration');
  };

  const handleGuest = async () => {
    await enterGuestMode();
    router.replace('/');
  };

  // Pulse ring animation
  const pulseScale = useRef(new Animated.Value(1)).current;
  const pulseOpacity = useRef(new Animated.Value(0.6)).current;
  useEffect(() => {
    const pulse = Animated.loop(
      Animated.sequence([
        Animated.parallel([
          Animated.timing(pulseScale, { toValue: 1.25, duration: 1800, useNativeDriver: true }),
          Animated.timing(pulseOpacity, { toValue: 0, duration: 1800, useNativeDriver: true }),
        ]),
        Animated.parallel([
          Animated.timing(pulseScale, { toValue: 1, duration: 0, useNativeDriver: true }),
          Animated.timing(pulseOpacity, { toValue: 0.6, duration: 0, useNativeDriver: true }),
        ]),
      ])
    );
    pulse.start();
    return () => pulse.stop();
  }, []);

  return (
    <ThemedView surface="card" style={styles.safeArea}>
      <SafeAreaView style={styles.safeAreaContainer}>
        <View style={styles.container}>

          {/* Main Hero Branding Section */}
          <FadeInView delay={0} style={styles.heroContainer}>
            <View style={styles.iconWrapper}>
              <View style={[styles.iconBackground, { backgroundColor: palette.secondary }]}>
                <Ionicons name="radio-outline" size={64} color={palette.primary} />
              </View>
              <Animated.View style={[styles.pulseRing, { borderColor: palette.secondary, transform: [{ scale: pulseScale }], opacity: pulseOpacity }]} />
            </View>
            <ThemedText type="hero" style={styles.title}>
              Risk<ThemedText type="hero" lightColor={palette.primary} darkColor={palette.primary}>Radar</ThemedText>
            </ThemedText>
            <ThemedText
              type="body"
              lightColor={palette.textSecondary}
              darkColor={palette.textSecondary}
              style={styles.subtitle}
            >
              Stay aware. Stay prepared.
            </ThemedText>
          </FadeInView>

          {/* Action Buttons */}
          <View style={styles.actionContainer}>
            <FadeInView delay={200}>
              <PrimaryButton
                label="Log In"
                onPress={handleLogin}
                leftIcon={<Ionicons name="log-in-outline" size={20} color={palette.white} style={styles.buttonIcon} />}
              />
            </FadeInView>

            <FadeInView delay={320}>
              <PrimaryButton
                label="Create Account"
                onPress={handleCreateAccount}
                leftIcon={<Ionicons name="person-add-outline" size={20} color={palette.primary} style={styles.buttonIcon} />}
                style={{ backgroundColor: palette.secondary }}
                textStyle={{ color: palette.primary }}
              />
            </FadeInView>
          </View>

          {/* Footer / Guest Mode */}
          <FadeInView delay={440} style={styles.footerContainer}>
            <View style={styles.dividerContainer}>
              <View style={[styles.divider, { backgroundColor: palette.border }]} />
              <ThemedText
                type="eyebrow"
                lightColor={palette.textSecondary}
                darkColor={palette.textSecondary}
                style={styles.dividerText}
              >
                OR
              </ThemedText>
              <View style={[styles.divider, { backgroundColor: palette.border }]} />
            </View>

            <TouchableOpacity
              style={styles.guestButton}
              onPress={handleGuest}
              activeOpacity={0.6}
            >
              <ThemedText
                type="body"
                lightColor={palette.textSecondary}
                darkColor={palette.textSecondary}
              >
                Continue as Guest
              </ThemedText>
              <Ionicons name="arrow-forward" size={16} color={palette.textSecondary} style={styles.guestIcon} />
            </TouchableOpacity>
          </FadeInView>

        </View>
      </SafeAreaView>
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
  },
  safeAreaContainer: {
    flex: 1,
  },
  container: {
    flex: 1,
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: Spacing.md,
    paddingTop: 60,
    paddingBottom: 40,
  },
  heroContainer: {
    alignItems: 'center',
    marginTop: 40,
  },
  iconWrapper: {
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: Spacing.xl,
    position: 'relative',
  },
  iconBackground: {
    width: 120,
    height: 120,
    borderRadius: 60,
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 2,
  },
  pulseRing: {
    position: 'absolute',
    width: 140,
    height: 140,
    borderRadius: 70,
    borderWidth: 2,
    zIndex: 1,
  },
  title: {
    marginBottom: Spacing.sm,
    letterSpacing: -1,
  },
  subtitle: {
    textAlign: 'center',
  },
  actionContainer: {
    width: '100%',
    paddingHorizontal: Spacing.sm,
  },
  buttonIcon: {
    marginRight: Spacing.sm,
  },
  footerContainer: {
    width: '100%',
    alignItems: 'center',
  },
  dividerContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    width: '80%',
    marginBottom: Spacing.lg,
  },
  divider: {
    flex: 1,
    height: 1,
  },
  dividerText: {
    paddingHorizontal: Spacing.md,
  },
  guestButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: Spacing.sm,
    paddingHorizontal: Spacing.md,
  },
  guestIcon: {
    marginLeft: Spacing.xs,
    marginTop: 2,
  },
});
