import React from 'react';
import { 
  Text, 
  View, 
  StyleSheet, 
  TouchableOpacity, 
  SafeAreaView,
} from "react-native";
import { useRouter } from "expo-router";
import { Ionicons } from '@expo/vector-icons';

import { Colors } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';

export default function MainScreen() {
  const router = useRouter();
  const scheme = useColorScheme() ?? 'light';
  const palette = Colors[scheme];

  const handleLogin = () => {
    router.push("/auth/login");
  };

  const handleCreateAccount = () => {
    router.push("/auth/registration");
  };

  const handleGuest = () => {
    router.push("/main/home");
  };

  return (
    <SafeAreaView style={[styles.safeArea, { backgroundColor: palette.card }]}>
      <View style={styles.container}>
        
        {/* Main Icon & Branding */}
        <View style={styles.heroContainer}>
          <View style={styles.iconWrapper}>
            <View style={[styles.iconBackground, { backgroundColor: palette.secondary }]}>
              <Ionicons name="radio-outline" size={64} color={palette.primary} />
            </View>
            <View style={[styles.pulseRing, { borderColor: palette.secondary }]} />
          </View>
          <Text style={[styles.title, { color: palette.text }]}>Risk<Text style={{ color: palette.primary }}>Radar</Text></Text>
          <Text style={[styles.subtitle, { color: palette.textSecondary }]}>Stay aware. Stay prepared.</Text>
        </View>

        {/* Action Buttons */}
        <View style={styles.actionContainer}>
          <TouchableOpacity 
            style={[styles.primaryButton, { backgroundColor: palette.primary, shadowColor: palette.primary }]} 
            onPress={handleLogin}
            activeOpacity={0.8}
          >
            <Ionicons name="log-in-outline" size={20} color={palette.white} style={styles.buttonIcon} />
            <Text style={styles.primaryButtonText}>Log In</Text>
          </TouchableOpacity>

          <TouchableOpacity 
            style={[styles.secondaryButton, { backgroundColor: palette.secondary }]}
            onPress={handleCreateAccount}
            activeOpacity={0.6}
          >
            <Ionicons name="person-add-outline" size={20} color={palette.primary} style={styles.buttonIcon} />
            <Text style={[styles.secondaryButtonText, { color: palette.primary }]}>Create Account</Text>
          </TouchableOpacity>
        </View>

        {/* Footer / Guest Mode */}
        <View style={styles.footerContainer}>
          <View style={styles.dividerContainer}>
            <View style={[styles.divider, { backgroundColor: palette.border }]} />
            <Text style={[styles.dividerText, { color: palette.textSecondary }]}>OR</Text>
            <View style={[styles.divider, { backgroundColor: palette.border }]} />
          </View>

          <TouchableOpacity 
            style={styles.guestButton} 
            onPress={handleGuest}
            activeOpacity={0.6}
          >
            <Text style={[styles.guestText, { color: palette.textSecondary }]}>Continue as Guest</Text>
            <Ionicons name="arrow-forward" size={16} color={palette.textSecondary} style={styles.guestIcon} />
          </TouchableOpacity>
        </View>

      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
  },
  container: {
    flex: 1,
    justifyContent: "space-between",
    alignItems: "center",
    paddingHorizontal: 24,
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
    marginBottom: 32,
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
    fontSize: 42,
    fontWeight: "800",
    marginBottom: 12,
    letterSpacing: -1,
  },
  subtitle: {
    fontSize: 18,
    textAlign: "center",
    fontWeight: "500",
  },
  actionContainer: {
    width: '100%',
    paddingHorizontal: 12,
  },
  primaryButton: {
    flexDirection: 'row',
    width: "100%",
    height: 56,
    borderRadius: 16,
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 16,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 4.65,
    elevation: 8,
  },
  buttonIcon: {
    marginRight: 8,
  },
  primaryButtonText: {
    color: "#FFFFFF",
    fontSize: 16,
    fontWeight: "700",
    letterSpacing: 0.5,
  },
  secondaryButton: {
    flexDirection: 'row',
    width: "100%",
    height: 56,
    borderRadius: 16,
    justifyContent: "center",
    alignItems: "center",
  },
  secondaryButtonText: {
    fontSize: 16,
    fontWeight: "700",
    letterSpacing: 0.5,
  },
  footerContainer: {
    width: '100%',
    alignItems: 'center',
  },
  dividerContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    width: '80%',
    marginBottom: 24,
  },
  divider: {
    flex: 1,
    height: 1,
  },
  dividerText: {
    paddingHorizontal: 16,
    fontSize: 12,
    fontWeight: '600',
  },
  guestButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    paddingHorizontal: 16,
  },
  guestText: {
    fontSize: 15,
    fontWeight: "600",
  },
  guestIcon: {
    marginLeft: 4,
    marginTop: 2,
  },
});