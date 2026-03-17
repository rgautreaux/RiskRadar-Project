import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  Platform,
  StatusBar
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { Colors } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';

export default function Home() {
  const router = useRouter();
  const scheme = useColorScheme() ?? 'light';
  const palette = Colors[scheme];
  const styles = getStyles(palette);
  const [zipCode, setZipCode] = useState('');

  // This state will eventually be driven by auth context
  const [isGuest] = useState(true);

  const handleSearch = () => {
    if (zipCode.length === 5) {
      console.log('Fetching reports for Zip Code:', zipCode);
      // Trigger report generation logic here
    }
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar barStyle={scheme === 'dark' ? 'light-content' : 'dark-content'} backgroundColor={palette.background} />

      {/* Header */}
      <View style={styles.header}>
        <View>
          <Text style={styles.greeting}>Welcome, {isGuest ? 'Guest' : 'User'}</Text>
          <Text style={styles.headerSubtitle}>Stay ahead of the weather</Text>
        </View>
        <TouchableOpacity
          style={styles.profileButton}
          onPress={() => isGuest ? router.replace('/auth/login') : console.log('Profile')}
        >
          <Ionicons name={isGuest ? 'log-in-outline' : 'person-circle-outline'} size={28} color={palette.primary} />
        </TouchableOpacity>
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
        {/* Search Section */}
        <View style={styles.searchSection}>
          <Text style={styles.sectionTitle}>Check Location Risk</Text>
          <Text style={styles.sectionSubtitle}>
            {isGuest
              ? 'Enter a zip code to see current weather and risk reports.'
              : 'Showing your home location. Enter a different zip code to check another area.'}
          </Text>

          <View style={styles.searchContainer}>
            <View style={styles.inputWrapper}>
              <Ionicons name="location-outline" size={20} color={palette.textSecondary} style={styles.inputIcon} />
              <TextInput
                style={styles.input}
                placeholder="Enter 5-digit Zip Code"
                placeholderTextColor={palette.textSecondary}
                keyboardType="number-pad"
                maxLength={5}
                value={zipCode}
                onChangeText={setZipCode}
              />
            </View>
            <TouchableOpacity
              style={[styles.searchButton, zipCode.length !== 5 && styles.searchButtonDisabled]}
              onPress={handleSearch}
              disabled={zipCode.length !== 5}
            >
              <Ionicons name="search" size={20} color={palette.white} />
            </TouchableOpacity>
          </View>
        </View>

        {/* Placeholder: Weather Summary */}
        <TouchableOpacity
          style={styles.card}
          onPress={() => router.push({ pathname: '/main/weather-report', params: { zipCode: zipCode || 'Unknown Location' } })}
        >
          <View style={styles.cardHeader}>
            <View style={styles.cardIconBox}>
              <Ionicons name="partly-sunny" size={24} color="#F59E0B" />
            </View>
            <Text style={styles.cardTitle}>Current Conditions</Text>
          </View>

          <View style={styles.placeholderBox}>
            <Text style={styles.placeholderText}>
              {zipCode.length === 5 ? `Results for ${zipCode}` : 'Awaiting Zip Code...'}
            </Text>
            <Text style={styles.placeholderSubtext}>
              {zipCode.length === 5 ? 'Tap to view full weather summary.' : 'Enter a zip code and tap here.'}
            </Text>
          </View>
        </TouchableOpacity>

        {/* Placeholder: Risk Summary */}
        <View style={styles.card}>
          <View style={styles.cardHeader}>
            <View style={[styles.cardIconBox, { backgroundColor: '#FEE2E2' }]}>
              <Ionicons name="warning-outline" size={24} color={palette.danger} />
            </View>
            <Text style={styles.cardTitle}>Risk Assessment</Text>
          </View>

          <View style={styles.placeholderContent}>
            <View style={styles.skeletonLine} />
            <View style={[styles.skeletonLine, { width: '80%' }]} />
            <View style={[styles.skeletonLine, { width: '60%' }]} />
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

function getStyles(palette: typeof Colors.light) {
  return StyleSheet.create({
    safeArea: {
      flex: 1,
      backgroundColor: palette.background,
    },
    header: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      paddingHorizontal: 24,
      paddingTop: Platform.OS === 'android' ? 16 : 0,
      paddingBottom: 16,
      backgroundColor: palette.card,
      borderBottomWidth: 1,
      borderBottomColor: palette.border,
    },
    greeting: {
      fontSize: 24,
      fontWeight: '700',
      color: palette.text,
    },
    headerSubtitle: {
      fontSize: 14,
      color: palette.textSecondary,
      marginTop: 2,
    },
    profileButton: {
      width: 44,
      height: 44,
      borderRadius: 22,
      backgroundColor: palette.secondary,
      justifyContent: 'center',
      alignItems: 'center',
    },
    scrollContent: {
      padding: 24,
      paddingBottom: 40,
    },
    searchSection: {
      marginBottom: 32,
    },
    sectionTitle: {
      fontSize: 20,
      fontWeight: '700',
      color: palette.text,
      marginBottom: 8,
    },
    sectionSubtitle: {
      fontSize: 14,
      color: palette.textSecondary,
      marginBottom: 16,
      lineHeight: 20,
    },
    searchContainer: {
      flexDirection: 'row',
      alignItems: 'center',
    },
    inputWrapper: {
      flex: 1,
      flexDirection: 'row',
      alignItems: 'center',
      backgroundColor: palette.card,
      borderWidth: 1,
      borderColor: palette.border,
      borderRadius: 16,
      height: 56,
      paddingHorizontal: 16,
      marginRight: 12,
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 1 },
      shadowOpacity: 0.05,
      shadowRadius: 2,
      elevation: 2,
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
    searchButton: {
      width: 56,
      height: 56,
      backgroundColor: palette.primary,
      borderRadius: 16,
      justifyContent: 'center',
      alignItems: 'center',
      shadowColor: palette.primary,
      shadowOffset: { width: 0, height: 4 },
      shadowOpacity: 0.3,
      shadowRadius: 4.65,
      elevation: 8,
    },
    searchButtonDisabled: {
      backgroundColor: palette.textSecondary,
      shadowOpacity: 0,
      elevation: 0,
    },
    card: {
      backgroundColor: palette.card,
      borderRadius: 24,
      padding: 20,
      marginBottom: 20,
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 4 },
      shadowOpacity: 0.05,
      shadowRadius: 12,
      elevation: 4,
      borderWidth: 1,
      borderColor: palette.border,
    },
    cardHeader: {
      flexDirection: 'row',
      alignItems: 'center',
      marginBottom: 16,
    },
    cardIconBox: {
      width: 48,
      height: 48,
      borderRadius: 16,
      backgroundColor: '#FEF3C7',
      justifyContent: 'center',
      alignItems: 'center',
      marginRight: 12,
    },
    cardTitle: {
      fontSize: 18,
      fontWeight: '700',
      color: palette.text,
    },
    placeholderBox: {
      backgroundColor: palette.surfaceMuted,
      borderRadius: 16,
      padding: 24,
      alignItems: 'center',
      borderWidth: 1,
      borderColor: palette.border,
      borderStyle: 'dashed',
    },
    placeholderText: {
      fontSize: 16,
      fontWeight: '600',
      color: palette.textSecondary,
      marginBottom: 4,
    },
    placeholderSubtext: {
      fontSize: 14,
      color: palette.textSecondary,
      textAlign: 'center',
    },
    placeholderContent: {
      backgroundColor: palette.surfaceMuted,
      borderRadius: 16,
      padding: 20,
    },
    skeletonLine: {
      height: 12,
      backgroundColor: palette.border,
      borderRadius: 6,
      marginBottom: 12,
      width: '100%',
    },
  });
}
