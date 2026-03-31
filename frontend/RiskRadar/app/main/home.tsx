import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  Platform,
  StatusBar,
  ActivityIndicator,
} from 'react-native';
import EmptyState from '@/components/ui/EmptyState';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { Colors } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { useAuth } from '@/contexts/auth-context';
import { apiFetch } from '@/utils/api';
import { API_BASE_URL } from '@/constants/api';

interface AlertStats {
  total: number;
  by_type: Record<string, number>;
  by_severity: Record<string, number>;
}

interface Summary {
  id: number;
  title: string;
  content: string;
  summary_type: string;
  region: string | null;
  generated_at: string;
}

export default function Home() {
  const router = useRouter();
  const scheme = useColorScheme() ?? 'light';
  const palette = Colors[scheme];
  const styles = getStyles(palette);
  const { user, isLoggedIn } = useAuth();
  const [zipCode, setZipCode] = useState(user?.zip_code ?? '');
  const [stats, setStats] = useState<AlertStats | null>(null);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [loadingStats, setLoadingStats] = useState(true);
  const [loadingSummary, setLoadingSummary] = useState(true);

  useEffect(() => {
    if (user?.zip_code) setZipCode(user.zip_code);
  }, [user?.zip_code]);

  useEffect(() => {
    (async () => {
      try {
        console.log('Fetching stats from:', API_BASE_URL + '/alerts/stats');
        const data = await apiFetch<AlertStats>('/alerts/stats');
        console.log('Stats loaded:', data);
        setStats(data);
      } catch (err) { console.error('Stats fetch failed:', err); }
      finally { setLoadingStats(false); }
    })();

    (async () => {
      try {
        const data = await apiFetch<Summary | null>('/summaries/latest');
        console.log('Summary loaded:', data);
        setSummary(data);
      } catch (err) { console.error('Summary fetch failed:', err); }
      finally { setLoadingSummary(false); }
    })();
  }, []);

  const handleSearch = () => {
    if (zipCode.length === 5) {
      router.push({ pathname: '/main/weather-report', params: { zipCode } });
    }
  };

  const displayName = isLoggedIn ? (user?.display_name ?? 'User') : 'Guest';

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar barStyle={scheme === 'dark' ? 'light-content' : 'dark-content'} backgroundColor={palette.background} />

      {/* Header */}
      <View style={styles.header}>
        <View>
          <Text style={styles.greeting}>Welcome, {displayName}</Text>
          <Text style={styles.headerSubtitle}>Stay ahead of the weather</Text>
        </View>
        <TouchableOpacity
          style={styles.profileButton}
          onPress={() => !isLoggedIn ? router.replace('/auth/login') : console.log('Profile')}
        >
          <Ionicons name={!isLoggedIn ? 'log-in-outline' : 'person-circle-outline'} size={28} color={palette.primary} />
        </TouchableOpacity>
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
        {/* Search Section */}
        <View style={styles.searchSection}>
          <Text style={styles.sectionTitle}>Check Location Risk</Text>
          <Text style={styles.sectionSubtitle}>
            {!isLoggedIn
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

        {/* Latest Summary Card */}
        <TouchableOpacity
          style={styles.card}
          onPress={() => router.push({ pathname: '/main/weather-report', params: { zipCode: zipCode || 'Unknown Location' } })}
        >
          <View style={styles.cardHeader}>
            <View style={styles.cardIconBox}>
              <Ionicons name="partly-sunny" size={24} color="#F59E0B" />
            </View>
            <Text style={styles.cardTitle}>Latest Summary</Text>
          </View>

          {loadingSummary ? (
            <ActivityIndicator color={palette.primary} style={{ paddingVertical: 24 }} />
          ) : summary ? (
            <View style={styles.summaryBox}>
              <Text style={styles.summaryTitle}>{summary.title}</Text>
              <Text style={styles.summaryText} numberOfLines={3}>{summary.content}</Text>
              <Text style={styles.summaryMeta}>
                Generated {new Date(summary.generated_at).toLocaleDateString()}
              </Text>
            </View>
          ) : (
            <EmptyState
              title={zipCode.length === 5 ? `Results for ${zipCode}` : 'Awaiting Zip Code...'}
              subtitle={zipCode.length === 5 ? 'Tap to view full weather summary.' : 'Enter a zip code above.'}
              style={styles.placeholderBox}
            />
          )}
        </TouchableOpacity>

        {/* Risk Assessment Card */}
        <View style={styles.card}>
          <View style={styles.cardHeader}>
            <View style={[styles.cardIconBox, { backgroundColor: '#FEE2E2' }]}>
              <Ionicons name="warning-outline" size={24} color={palette.danger} />
            </View>
            <Text style={styles.cardTitle}>Risk Assessment</Text>
          </View>

          {loadingStats ? (
            <ActivityIndicator color={palette.primary} style={{ paddingVertical: 24 }} />
          ) : stats ? (
            <View style={styles.statsContainer}>
              <View style={styles.statRow}>
                <Text style={styles.statLabel}>Total Active Alerts</Text>
                <Text style={styles.statValue}>{stats.total}</Text>
              </View>
              {Object.entries(stats.by_severity).map(([severity, count]) => (
                <View key={severity} style={styles.statRow}>
                  <Text style={styles.statLabel}>{severity}</Text>
                  <Text style={styles.statValue}>{count}</Text>
                </View>
              ))}
            </View>
          ) : (
            <EmptyState
              title="No data available"
              subtitle="Make sure the backend is running."
              style={styles.placeholderContent}
            />
          )}
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
    summaryBox: {
      backgroundColor: palette.surfaceMuted,
      borderRadius: 16,
      padding: 16,
    },
    summaryTitle: {
      fontSize: 16,
      fontWeight: '600',
      color: palette.text,
      marginBottom: 8,
    },
    summaryText: {
      fontSize: 14,
      lineHeight: 20,
      color: palette.textSecondary,
    },
    summaryMeta: {
      fontSize: 12,
      color: palette.textSecondary,
      marginTop: 8,
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
      alignItems: 'center',
    },
    statsContainer: {
      backgroundColor: palette.surfaceMuted,
      borderRadius: 16,
      padding: 16,
    },
    statRow: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      paddingVertical: 8,
      borderBottomWidth: 1,
      borderBottomColor: palette.border,
    },
    statLabel: {
      fontSize: 14,
      color: palette.textSecondary,
      textTransform: 'capitalize',
    },
    statValue: {
      fontSize: 14,
      fontWeight: '700',
      color: palette.text,
    },
  });
}
