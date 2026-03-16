import React from 'react';
import { 
  Text, 
  View, 
  StyleSheet, 
  TouchableOpacity, 
  SafeAreaView,
  StatusBar,
  Dimensions
} from "react-native";
import { useRouter } from "expo-router";
import { Ionicons } from '@expo/vector-icons';

const { width } = Dimensions.get('window');

export default function MainScreen() {
  const router = useRouter();

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
    <SafeAreaView style={styles.safeArea}>
      <StatusBar barStyle="dark-content" backgroundColor="#FFFFFF" />
      <View style={styles.container}>
        
        {/* Main Icon & Branding */}
        <View style={styles.heroContainer}>
          <View style={styles.iconWrapper}>
            <View style={styles.iconBackground}>
              <Ionicons name="radio-outline" size={64} color="#4F46E5" />
            </View>
            <View style={styles.pulseRing} />
          </View>
          <Text style={styles.title}>Risk<Text style={styles.titleHighlight}>Radar</Text></Text>
          <Text style={styles.subtitle}>Stay aware. Stay prepared.</Text>
        </View>

        {/* Action Buttons */}
        <View style={styles.actionContainer}>
          <TouchableOpacity 
            style={styles.primaryButton} 
            onPress={handleLogin}
            activeOpacity={0.8}
          >
            <Ionicons name="log-in-outline" size={20} color="#FFFFFF" style={styles.buttonIcon} />
            <Text style={styles.primaryButtonText}>Log In</Text>
          </TouchableOpacity>

          <TouchableOpacity 
            style={styles.secondaryButton} 
            onPress={handleCreateAccount}
            activeOpacity={0.6}
          >
            <Ionicons name="person-add-outline" size={20} color="#4F46E5" style={styles.buttonIcon} />
            <Text style={styles.secondaryButtonText}>Create Account</Text>
          </TouchableOpacity>
        </View>

        {/* Footer / Guest Mode */}
        <View style={styles.footerContainer}>
          <View style={styles.dividerContainer}>
            <View style={styles.divider} />
            <Text style={styles.dividerText}>OR</Text>
            <View style={styles.divider} />
          </View>

          <TouchableOpacity 
            style={styles.guestButton} 
            onPress={handleGuest}
            activeOpacity={0.6}
          >
            <Text style={styles.guestText}>Continue as Guest</Text>
            <Ionicons name="arrow-forward" size={16} color="#6B7280" style={styles.guestIcon} />
          </TouchableOpacity>
        </View>

      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#FFFFFF',
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
    backgroundColor: '#EEF2FF',
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
    borderColor: '#EEF2FF',
    zIndex: 1,
  },
  title: {
    fontSize: 42,
    fontWeight: "800",
    color: "#111827",
    marginBottom: 12,
    letterSpacing: -1,
  },
  titleHighlight: {
    color: '#4F46E5',
  },
  subtitle: {
    fontSize: 18,
    color: "#6B7280",
    textAlign: "center",
    fontWeight: "500",
  },
  actionContainer: {
    width: '100%',
    paddingHorizontal: 12,
  },
  primaryButton: {
    flexDirection: 'row',
    backgroundColor: "#4F46E5",
    width: "100%",
    height: 56,
    borderRadius: 16,
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 16,
    shadowColor: '#4F46E5',
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
    backgroundColor: "#EEF2FF",
    width: "100%",
    height: 56,
    borderRadius: 16,
    justifyContent: "center",
    alignItems: "center",
  },
  secondaryButtonText: {
    color: "#4F46E5",
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
    backgroundColor: '#E5E7EB',
  },
  dividerText: {
    color: '#9CA3AF',
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
    color: "#6B7280",
    fontWeight: "600",
  },
  guestIcon: {
    marginLeft: 4,
    marginTop: 2,
  },
});