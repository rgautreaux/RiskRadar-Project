import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  SafeAreaView,
  ScrollView,
  Pressable,
  Image,
} from 'react-native';
import { PrimaryButton } from '@/components/ui/PrimaryButton';

const brandLogo = require('@/assets/icons/branding/RiskRadar_STND_Logo.png');
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { Colors } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { useAuth } from '@/contexts/auth-context';

export default function RegistrationScreen() {
  const router = useRouter();
  const scheme = useColorScheme() ?? 'light';
  const palette = Colors[scheme];
  const styles = getStyles(palette);
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [zipCode, setZipCode] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState<{
    fullName?: string;
    email?: string;
    zipCode?: string;
    password?: string;
    confirmPassword?: string;
    form?: string;
  }>({});
  const { register } = useAuth();

  const validateForm = () => {
    const newErrors: typeof errors = {};
    let isValid = true;
    
    if (!fullName.trim()) {
      newErrors.fullName = 'Full name is required.';
      isValid = false;
    }
    
    if (!email.trim()) {
      newErrors.email = 'Email address is required.';
      isValid = false;
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      newErrors.email = 'Please enter a valid email address.';
      isValid = false;
    }
    
    if (zipCode && (zipCode.length !== 5 || !/^\d{5}$/.test(zipCode))) {
      newErrors.zipCode = 'Please enter a valid 5-digit zip code.';
      isValid = false;
    }
    
    if (!password) {
      newErrors.password = 'Password is required.';
      isValid = false;
    } else if (password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters.';
      isValid = false;
    }
    
    if (!confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password.';
      isValid = false;
    } else if (password !== confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match.';
      isValid = false;
    }
    
    setErrors(newErrors);
    return isValid;
  };

  const handleRegister = async () => {
    if (!validateForm()) return;
    setErrors({});
    setIsSubmitting(true);
    try {
      await register(fullName, email, password, zipCode || undefined);
      router.replace('/(tabs)');
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : '';
      let message = 'Registration failed. Please try again.';
      if (errorMessage.includes('already registered')) {
        message = 'An account with this email already exists.';
      } else if (errorMessage.includes('Failed to fetch') || errorMessage.includes('Network request failed')) {
        message = 'Cannot connect to server. Make sure the backend is running.';
      } else if (errorMessage.includes('Too many requests')) {
        message = 'Too many attempts. Please wait a moment and try again.';
      } else if (errorMessage.includes('value is not a valid email')) {
        message = 'Please enter a valid email address.';
      } else if (errorMessage.includes('Password must be at least')) {
        message = 'Password must be at least 6 characters.';
      }
      // Don't pass raw backend errors to the UI — use the safe default above
      setErrors({ form: message });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardAvoidingView}
      >
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
        >
          <TouchableOpacity
            style={styles.backButton}
            onPress={() => router.replace('/')}
            accessibilityRole="button"
            accessibilityLabel="Go back"
          >
            <Ionicons name="arrow-back" size={24} color={palette.text} />
          </TouchableOpacity>

          <View style={styles.headerContainer}>
            <Image source={brandLogo} style={{ width: 80, height: 80, marginBottom: 20 }} resizeMode="contain" />
            <Text style={styles.title}>Create Account</Text>
            <Text style={styles.subtitle}>Join RiskRadar to stay aware and prepared</Text>
          </View>

          <View style={styles.formContainer}>
            {errors.form ? <Text style={styles.formError}>{errors.form}</Text> : null}

            <View style={styles.inputGroup}>
              <Text style={styles.label}>Full Name</Text>
              <View style={[styles.inputContainer, errors.fullName && styles.inputError]}>
                <Ionicons name="person-outline" size={20} color={palette.textSecondary} style={styles.inputIcon} />
                <TextInput
                  style={styles.input}
                  placeholder="Enter your full name"
                  placeholderTextColor={palette.textSecondary}
                  autoCapitalize="words"
                  value={fullName}
                  onChangeText={(text) => {
                    setFullName(text);
                    if (errors.fullName) setErrors((prev) => ({ ...prev, fullName: undefined }));
                  }}
                />
              </View>
              {errors.fullName ? <Text style={styles.errorText}>{errors.fullName}</Text> : null}
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>Email Address</Text>
              <View style={[styles.inputContainer, errors.email && styles.inputError]}>
                <Ionicons name="mail-outline" size={20} color={palette.textSecondary} style={styles.inputIcon} />
                <TextInput
                  style={styles.input}
                  placeholder="Enter your email"
                  placeholderTextColor={palette.textSecondary}
                  keyboardType="email-address"
                  autoCapitalize="none"
                  value={email}
                  onChangeText={(text) => {
                    setEmail(text);
                    if (errors.email) setErrors((prev) => ({ ...prev, email: undefined }));
                  }}
                />
              </View>
              {errors.email ? <Text style={styles.errorText}>{errors.email}</Text> : null}
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>Home Zip Code</Text>
              <View style={[styles.inputContainer, errors.zipCode && styles.inputError]}>
                <Ionicons name="location-outline" size={20} color={palette.textSecondary} style={styles.inputIcon} />
                <TextInput
                  style={styles.input}
                  placeholder="Enter 5-digit zip code"
                  placeholderTextColor={palette.textSecondary}
                  keyboardType="number-pad"
                  maxLength={5}
                  value={zipCode}
                  onChangeText={(text) => {
                    setZipCode(text);
                    if (errors.zipCode) setErrors((prev) => ({ ...prev, zipCode: undefined }));
                  }}
                />
              </View>
              {errors.zipCode ? <Text style={styles.errorText}>{errors.zipCode}</Text> : null}
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>Password</Text>
              <View style={[styles.inputContainer, errors.password && styles.inputError]}>
                <Ionicons name="lock-closed-outline" size={20} color={palette.textSecondary} style={styles.inputIcon} />
                <TextInput
                  style={styles.input}
                  placeholder="Create a password"
                  placeholderTextColor={palette.textSecondary}
                  secureTextEntry={!showPassword}
                  value={password}
                  onChangeText={(text) => {
                    setPassword(text);
                    if (errors.password) setErrors((prev) => ({ ...prev, password: undefined }));
                  }}
                />
                <Pressable
                  onPress={() => setShowPassword(!showPassword)}
                  style={styles.eyeIcon}
                  accessibilityRole="button"
                  accessibilityLabel={showPassword ? 'Hide password' : 'Show password'}
                >
                  <Ionicons
                    name={showPassword ? 'eye-off-outline' : 'eye-outline'}
                    size={20}
                    color={palette.textSecondary}
                  />
                </Pressable>
              </View>
              {errors.password ? <Text style={styles.errorText}>{errors.password}</Text> : null}
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>Confirm Password</Text>
              <View style={[styles.inputContainer, errors.confirmPassword && styles.inputError]}>
                <Ionicons name="shield-checkmark-outline" size={20} color={palette.textSecondary} style={styles.inputIcon} />
                <TextInput
                  style={styles.input}
                  placeholder="Confirm your password"
                  placeholderTextColor={palette.textSecondary}
                  secureTextEntry={!showConfirmPassword}
                  value={confirmPassword}
                  onChangeText={(text) => {
                    setConfirmPassword(text);
                    if (errors.confirmPassword) setErrors((prev) => ({ ...prev, confirmPassword: undefined }));
                  }}
                />
                <Pressable
                  onPress={() => setShowConfirmPassword(!showConfirmPassword)}
                  style={styles.eyeIcon}
                  accessibilityRole="button"
                  accessibilityLabel={showConfirmPassword ? 'Hide password' : 'Show password'}
                >
                  <Ionicons
                    name={showConfirmPassword ? 'eye-off-outline' : 'eye-outline'}
                    size={20}
                    color={palette.textSecondary}
                  />
                </Pressable>
              </View>
              {errors.confirmPassword ? <Text style={styles.errorText}>{errors.confirmPassword}</Text> : null}
            </View>

            <View style={styles.termsContainer}>
              <Text style={styles.termsText}>
                By creating an account, you agree to our{' '}
                <Text style={styles.termsLink}>Terms of Service</Text> and{' '}
                <Text style={styles.termsLink}>Privacy Policy</Text>
              </Text>
            </View>

            <PrimaryButton
              label={isSubmitting ? '...' : 'Create Account'}
              onPress={handleRegister}
              disabled={isSubmitting}
              loading={isSubmitting}
            />
          </View>

          <View style={styles.footerContainer}>
            <Text style={styles.footerText}>Already have an account? </Text>
            <TouchableOpacity onPress={() => router.push('/auth/login')}>
              <Text style={styles.loginText}>Log in</Text>
            </TouchableOpacity>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

function getStyles(palette: typeof Colors.light | typeof Colors.dark) {
  return StyleSheet.create({
    safeArea: {
      flex: 1,
      backgroundColor: palette.card,
    },
    keyboardAvoidingView: {
      flex: 1,
    },
    scrollContent: {
      flexGrow: 1,
      paddingHorizontal: 24,
      paddingTop: 20,
      paddingBottom: 40,
    },
    backButton: {
      width: 40,
      height: 40,
      borderRadius: 20,
      backgroundColor: palette.surfaceMuted,
      justifyContent: 'center',
      alignItems: 'center',
      marginBottom: 24,
    },
    headerContainer: {
      marginBottom: 32,
    },
    title: {
      fontSize: 28,
      fontWeight: '700',
      color: palette.text,
      marginBottom: 8,
      letterSpacing: -0.5,
    },
    subtitle: {
      fontSize: 15,
      color: palette.textSecondary,
    },
    formContainer: {
      width: '100%',
    },
    inputGroup: {
      marginBottom: 20,
    },
    label: {
      fontSize: 14,
      fontWeight: '500',
      color: palette.text,
      marginBottom: 8,
      marginLeft: 4,
    },
    inputContainer: {
      flexDirection: 'row',
      alignItems: 'center',
      backgroundColor: palette.surfaceMuted,
      borderWidth: 1,
      borderColor: palette.border,
      borderRadius: 16,
      paddingHorizontal: 16,
      height: 56,
    },
    inputIcon: {
      marginRight: 12,
    },
    input: {
      flex: 1,
      fontSize: 16,
      color: palette.text,
      height: '100%',
    },
    eyeIcon: {
      padding: 8,
    },
    errorText: {
      color: palette.danger,
      fontSize: 12,
      marginTop: 4,
      marginLeft: 4,
    },
    formError: {
      color: palette.danger,
      fontSize: 14,
      textAlign: 'center',
      marginBottom: 16,
    },
    inputError: {
      borderColor: palette.danger,
    },
    termsContainer: {
      marginBottom: 24,
      marginTop: 8,
    },
    termsText: {
      color: palette.textSecondary,
      fontSize: 13,
      lineHeight: 20,
      textAlign: 'center',
    },
    termsLink: {
      color: palette.primary,
      fontWeight: '500',
    },
    footerContainer: {
      flexDirection: 'row',
      justifyContent: 'center',
      alignItems: 'center',
      marginTop: 32,
    },
    footerText: {
      fontSize: 15,
      color: palette.textSecondary,
    },
    loginText: {
      fontSize: 15,
      color: palette.primary,
      fontWeight: '600',
    },
  });
}
