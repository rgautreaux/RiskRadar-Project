import React from 'react';
import {
  StyleSheet,
  TouchableOpacity,
  SafeAreaView,
  View,
} from "react-native";
import { useRouter } from "expo-router";
import { Ionicons } from '@expo/vector-icons';
import { PrimaryButton } from '@/components/ui/PrimaryButton';

import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { Colors, Spacing, Radius, Shadows } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { useAuth } from '@/contexts/auth-context';

export default function HomeScreen() {
  const router = useRouter();
  const scheme = useColorScheme() ?? 'light';
  const palette = Colors[scheme];
  const { isLoggedIn, logout } = useAuth();

  const handleLogin = () => {
    router.push("/auth/login");
  };

  const handleCreateAccount = () => {
    router.push("/auth/registration");
  };

  const handleGuest = () => {
    router.replace("/main/home");
  };

  const handleLogout = async () => {
    await logout();
  };

  // If logged in, go straight to main home
  if (isLoggedIn) {
    return (
      <ThemedView surface="card" style={styles.safeArea}>
        <SafeAreaView style={styles.safeAreaContainer}>
          <View style={styles.container}>
            <View style={styles.heroContainer}>
              <View style={styles.iconWrapper}>
                <View style={[styles.iconBackground, { backgroundColor: palette.secondary }]}>
                  <Ionicons name="radio-outline" size={64} color={palette.primary} />
                </View>
                <View style={[styles.pulseRing, { borderColor: palette.secondary }]} />
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
            </View>
            <View style={styles.actionContainer}>
              <TouchableOpacity
                style={[styles.primaryButton, { backgroundColor: palette.primary, shadowColor: palette.primary }]}
                onPress={() => router.replace("/main/home")}
                activeOpacity={0.8}
              >
                <Ionicons name="home-outline" size={20} color={palette.white} style={styles.buttonIcon} />
                <ThemedText type="cardTitle" lightColor={palette.white} darkColor={palette.white}>
                  Go to Dashboard
                </ThemedText>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.secondaryButton, { backgroundColor: palette.secondary }]}
                onPress={handleLogout}
                activeOpacity={0.6}
              >
                <Ionicons name="log-out-outline" size={20} color={palette.primary} style={styles.buttonIcon} />
                <ThemedText type="cardTitle" lightColor={palette.primary} darkColor={palette.primary}>
                  Log Out
                </ThemedText>
              </TouchableOpacity>
            </View>
          </View>
        </SafeAreaView>
      </ThemedView>
    );
  }

  return (
    <ThemedView surface="card" style={styles.safeArea}>
      <SafeAreaView style={styles.safeAreaContainer}>
        <View style={styles.container}>
          
          {/* Main Hero Branding Section */}
          <View style={styles.heroContainer}>
            <View style={styles.iconWrapper}>
              <View style={[styles.iconBackground, { backgroundColor: palette.secondary }]}>
                <Ionicons name="radio-outline" size={64} color={palette.primary} />
              </View>
              <View style={[styles.pulseRing, { borderColor: palette.secondary }]} />
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
          </View>

          {/* Action Buttons */}
          <View style={styles.actionContainer}>
            <PrimaryButton
              label="Log In"
              onPress={handleLogin}
              leftIcon={<Ionicons name="log-in-outline" size={20} color={palette.white} style={styles.buttonIcon} />}
            />

            <PrimaryButton
              label="Create Account"
              onPress={handleCreateAccount}
              leftIcon={<Ionicons name="person-add-outline" size={20} color={palette.primary} style={styles.buttonIcon} />}
              style={{ backgroundColor: palette.secondary }}
              textStyle={{ color: palette.primary }}
            />
          </View>

          {/* Footer / Guest Mode */}
          <View style={styles.footerContainer}>
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
          </View>

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
    justifyContent: "space-between",
    alignItems: "center",
    paddingHorizontal: Spacing.md,
    paddingTop: 60,
    paddingBottom: 40,
  },
  heroContainer: {
    alignItems: "center",
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
    textAlign: "center",
  },
  actionContainer: {
    width: '100%',
    paddingHorizontal: Spacing.sm,
  },
  primaryButton: {
    flexDirection: 'row',
    width: "100%",
    height: 56,
    borderRadius: Radius.button,
    justifyContent: "center",
    alignItems: "center",
    marginBottom: Spacing.md,
    ...Shadows.card,
  },
  buttonIcon: {
    marginRight: Spacing.sm,
  },
  secondaryButton: {
    flexDirection: 'row',
    width: "100%",
    height: 56,
    borderRadius: Radius.button,
    justifyContent: "center",
    alignItems: "center",
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