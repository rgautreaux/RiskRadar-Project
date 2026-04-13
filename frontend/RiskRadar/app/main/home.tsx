import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  StatusBar,
  Keyboard,
  Image,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { Colors, Spacing, Radius, Shadows, Typography, SafeArea } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { useAuth } from '@/contexts/auth-context';
import { apiFetch } from '@/utils/api';
import { StateView } from '@/components/ui/state-view';

const brandLogo = require('@/assets/icons/branding/RiskRadar_STND_Logo.png');

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

interface AutocompleteResult {
  label: string;
  city: string;
  state: string;
}

export default function Home() {
  const router = useRouter();
  const scheme = useColorScheme() ?? 'light';
  const palette = Colors[scheme];
  const styles = getStyles(palette);
  const { user, isLoggedIn } = useAuth();
  const [searchQuery, setSearchQuery] = useState(user?.zip_code ?? '');
  const [suggestions, setSuggestions] = useState<AutocompleteResult[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [stats, setStats] = useState<AlertStats | null>(null);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [loadingStats, setLoadingStats] = useState(true);
  const [loadingSummary, setLoadingSummary] = useState(true);
  const [errorStats, setErrorStats] = useState<string | null>(null);
  const [errorSummary, setErrorSummary] = useState<string | null>(null);
  const autocompleteTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (user?.zip_code) setSearchQuery(user.zip_code);
  }, [user?.zip_code]);

  useEffect(() => {
    (async () => {
      try {
        setErrorStats(null);
        const data = await apiFetch<AlertStats>('/alerts/stats');
        setStats(data);
      } catch {
        setErrorStats('Failed to load risk assessment data');
      }
      finally { setLoadingStats(false); }
    })();

    (async () => {
      try {
        setErrorSummary(null);
        const data = await apiFetch<Summary | null>('/summaries/latest');
        setSummary(data);
      } catch {
        setErrorSummary('Failed to load latest summary');
      }
      finally { setLoadingSummary(false); }
    })();
  }, []);

  const isZip = (q: string) => /^\d{5}$/.test(q.trim());

  const fetchAutocomplete = useCallback(async (text: string) => {
    if (text.length < 2 || isZip(text)) {
      setSuggestions([]);
      setShowSuggestions(false);
      return;
    }
    try {
      const data = await apiFetch<AutocompleteResult[]>(
        `/location/autocomplete?q=${encodeURIComponent(text)}`
      );
      setSuggestions(data);
      setShowSuggestions(data.length > 0);
    } catch {
      setSuggestions([]);
      setShowSuggestions(false);
    }
  }, []);

  const handleQueryChange = (text: string) => {
    setSearchQuery(text);
    if (autocompleteTimer.current) clearTimeout(autocompleteTimer.current);
    autocompleteTimer.current = setTimeout(() => fetchAutocomplete(text), 300);
  };

  const handleSelectSuggestion = (suggestion: AutocompleteResult) => {
    setSearchQuery(suggestion.label);
    setSuggestions([]);
    setShowSuggestions(false);
    Keyboard.dismiss();
    router.push({ pathname: '/main/weather-report', params: { query: suggestion.label } });
  };

  const handleSearch = () => {
    const q = searchQuery.trim();
    if (q.length >= 2) {
      setShowSuggestions(false);
      Keyboard.dismiss();
      router.push({ pathname: '/main/weather-report', params: { query: q } });
    }
  };

  const canSearch = searchQuery.trim().length >= 2;
  const displayName = isLoggedIn ? (user?.display_name ?? 'User') : 'Guest';

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar barStyle="light-content" backgroundColor={palette.primaryDark} />

      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerLeft}>
          <Image source={brandLogo} style={styles.headerLogo} resizeMode="contain" />
          <View>
            <Text style={styles.greeting}>Welcome, {displayName}</Text>
            <Text style={styles.headerSubtitle}>Stay ahead of environmental risks</Text>
          </View>
        </View>
        <View style={styles.headerActions}>
          <TouchableOpacity
            style={styles.settingsButton}
            onPress={() => router.push('/main/settings')}
            accessibilityRole="button"
            accessibilityLabel="Settings"
          >
            <Ionicons name="settings-outline" size={24} color="rgba(255, 255, 255, 0.7)" />
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.profileButton}
            onPress={() => !isLoggedIn ? router.replace('/auth/login') : router.push('/main/settings')}
            accessibilityRole="button"
            accessibilityLabel={isLoggedIn ? 'Profile' : 'Log in'}
          >
            <Ionicons name={!isLoggedIn ? 'log-in-outline' : 'person-circle-outline'} size={28} color={palette.white} />
          </TouchableOpacity>
        </View>
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
        {/* Search Section */}
        <View style={styles.searchSection}>
          <Text style={styles.sectionTitle}>Check Location Risk</Text>
          <Text style={styles.sectionSubtitle}>
            {!isLoggedIn
              ? 'Enter a city name or zip code to see current weather and risk reports.'
              : 'Showing your home location. Search a different city or zip code to check another area.'}
          </Text>

          <View style={styles.searchContainer}>
            <View style={styles.inputWrapper}>
              <Ionicons name="location-outline" size={20} color={palette.textSecondary} style={styles.inputIcon} />
              <TextInput
                style={styles.input}
                placeholder="City, State or Zip Code"
                placeholderTextColor={palette.textSecondary}
                autoCapitalize="words"
                autoCorrect={false}
                returnKeyType="search"
                onSubmitEditing={handleSearch}
                value={searchQuery}
                onChangeText={handleQueryChange}
                onFocus={() => { if (suggestions.length > 0) setShowSuggestions(true); }}
              />
              {searchQuery.length > 0 && (
                <TouchableOpacity
                  onPress={() => { setSearchQuery(''); setSuggestions([]); setShowSuggestions(false); }}
                  accessibilityRole="button"
                  accessibilityLabel="Clear search"
                  hitSlop={{ top: 12, bottom: 12, left: 12, right: 12 }}
                >
                  <Ionicons name="close-circle" size={18} color={palette.textSecondary} />
                </TouchableOpacity>
              )}
            </View>
            <TouchableOpacity
              style={[styles.searchButton, !canSearch && styles.searchButtonDisabled]}
              onPress={handleSearch}
              disabled={!canSearch}
              accessibilityRole="button"
              accessibilityLabel="Search location"
              accessibilityState={{ disabled: !canSearch }}
            >
              <Ionicons name="search" size={20} color={palette.white} />
            </TouchableOpacity>
          </View>

          {/* Autocomplete suggestions */}
          {showSuggestions && suggestions.length > 0 && (
            <View style={styles.suggestionsContainer}>
              {suggestions.map((s, i) => (
                <TouchableOpacity
                  key={`${s.label}-${i}`}
                  style={[styles.suggestionRow, i < suggestions.length - 1 && styles.suggestionBorder]}
                  onPress={() => handleSelectSuggestion(s)}
                >
                  <Ionicons name="location-outline" size={16} color={palette.primary} style={{ marginRight: Spacing.sm }} />
                  <Text style={styles.suggestionText}>{s.label}</Text>
                </TouchableOpacity>
              ))}
            </View>
          )}
        </View>

        {/* Latest Summary Card */}
        <TouchableOpacity
          style={styles.card}
          onPress={() => router.push({ pathname: '/main/weather-report', params: { query: searchQuery || 'Unknown Location' } })}
        >
          <View style={styles.cardHeader}>
            <View style={styles.cardIconBox}>
              <Ionicons name="partly-sunny" size={24} color={palette.warning} />
            </View>
            <Text style={styles.cardTitle}>Latest Summary</Text>
          </View>

          <StateView
            state={loadingSummary ? 'loading' : errorSummary ? 'error' : summary ? 'success' : 'empty'}
            loadingText="Loading summary..."
            emptyText={searchQuery.trim().length >= 2 ? `No summary available for ${searchQuery}` : 'Search a city or zip code to see summaries'}
            emptyIcon="document-outline"
            errorText={errorSummary || 'Failed to load summary'}
            onRetry={() => {
              setLoadingSummary(true);
              setErrorSummary(null);
              (async () => {
                try {
                  const data = await apiFetch<Summary | null>('/summaries/latest');
                  setSummary(data);
                } catch {
                  setErrorSummary('Failed to load latest summary');
                } finally {
                  setLoadingSummary(false);
                }
              })();
            }}
          >
            <View style={styles.summaryBox}>
              <Text style={styles.summaryTitle}>{summary?.title}</Text>
              <Text style={styles.summaryText} numberOfLines={3}>{summary?.content}</Text>
              <Text style={styles.summaryMeta}>
                Generated {summary ? new Date(summary.generated_at).toLocaleDateString() : ''}
              </Text>
            </View>
          </StateView>
        </TouchableOpacity>

        {/* Risk Assessment Card */}
        <View style={styles.card}>
          <View style={styles.cardHeader}>
            <View style={[styles.cardIconBox, { backgroundColor: palette.surfaceMuted }]}>
              <Ionicons name="warning-outline" size={24} color={palette.danger} />
            </View>
            <Text style={styles.cardTitle}>Risk Assessment</Text>
          </View>

          <StateView
            state={loadingStats ? 'loading' : errorStats ? 'error' : stats ? 'success' : 'empty'}
            loadingText="Loading risk data..."
            emptyText="No risk data available"
            emptyIcon="stats-chart-outline"
            errorText={errorStats || 'Failed to load risk data'}
            onRetry={() => {
              setLoadingStats(true);
              setErrorStats(null);
              (async () => {
                try {
                  const data = await apiFetch<AlertStats>('/alerts/stats');
                  setStats(data);
                } catch {
                  setErrorStats('Failed to load risk assessment data');
                } finally {
                  setLoadingStats(false);
                }
              })();
            }}
          >
            <View style={styles.statsContainer}>
              <View style={styles.statRow}>
                <Text style={styles.statLabel}>Total Active Alerts</Text>
                <Text style={styles.statValue}>{stats?.total}</Text>
              </View>
              {stats && Object.entries(stats.by_severity).map(([severity, count]) => (
                <View key={severity} style={styles.statRow}>
                  <Text style={styles.statLabel}>{severity}</Text>
                  <Text style={styles.statValue}>{count}</Text>
                </View>
              ))}
            </View>
          </StateView>
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
      paddingHorizontal: Spacing.lg,
      paddingTop: SafeArea.paddingTop,
      paddingBottom: Spacing.md,
      backgroundColor: palette.primaryDark,
    },
    headerLeft: {
      flexDirection: 'row',
      alignItems: 'center',
      flex: 1,
    },
    headerLogo: {
      width: 40,
      height: 40,
      marginRight: Spacing.sm,
    },
    greeting: {
      ...Typography.title,
      fontSize: 24,
      color: palette.white,
    },
    headerSubtitle: {
      ...Typography.meta,
      fontSize: 14,
      color: 'rgba(255, 255, 255, 0.7)',
      marginTop: 2,
    },
    headerActions: {
      flexDirection: 'row',
      alignItems: 'center',
    },
    settingsButton: {
      width: 44,
      height: 44,
      justifyContent: 'center',
      alignItems: 'center',
      marginRight: Spacing.sm,
    },
    profileButton: {
      width: 44,
      height: 44,
      borderRadius: 22,
      backgroundColor: 'rgba(255, 255, 255, 0.15)',
      justifyContent: 'center',
      alignItems: 'center',
    },
    scrollContent: {
      padding: Spacing.lg,
      paddingBottom: Spacing.xxl,
    },
    searchSection: {
      marginBottom: Spacing.xl,
    },
    sectionTitle: {
      ...Typography.sectionLabel,
      color: palette.text,
      marginBottom: Spacing.sm,
    },
    sectionSubtitle: {
      ...Typography.meta,
      fontSize: 14,
      color: palette.textSecondary,
      marginBottom: Spacing.md,
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
      borderRadius: Radius.md,
      height: 56,
      paddingHorizontal: Spacing.md,
      marginRight: Spacing.sm,
      ...Shadows.card,
    },
    inputIcon: {
      marginRight: Spacing.sm,
    },
    input: {
      flex: 1,
      ...Typography.cardHeading,
      fontWeight: '400',
      color: palette.text,
      height: '100%',
    },
    searchButton: {
      width: 56,
      height: 56,
      backgroundColor: palette.primary,
      borderRadius: Radius.md,
      justifyContent: 'center',
      alignItems: 'center',
      ...Shadows.card,
    },
    searchButtonDisabled: {
      backgroundColor: palette.textSecondary,
      shadowOpacity: 0,
      elevation: 0,
    },
    suggestionsContainer: {
      marginTop: Spacing.sm,
      backgroundColor: palette.card,
      borderRadius: Radius.sm,
      borderWidth: 1,
      borderColor: palette.border,
      overflow: 'hidden',
      ...Shadows.card,
    },
    suggestionRow: {
      flexDirection: 'row',
      alignItems: 'center',
      paddingVertical: Spacing.sm + 4,
      paddingHorizontal: Spacing.md,
    },
    suggestionBorder: {
      borderBottomWidth: 1,
      borderBottomColor: palette.border,
    },
    suggestionText: {
      ...Typography.body,
      color: palette.text,
      flex: 1,
    },
    card: {
      backgroundColor: palette.card,
      borderRadius: Radius.lg,
      padding: Spacing.md + 4,
      marginBottom: Spacing.md + 4,
      ...Shadows.card,
      borderWidth: 1,
      borderColor: palette.border,
    },
    cardHeader: {
      flexDirection: 'row',
      alignItems: 'center',
      marginBottom: Spacing.md,
    },
    cardIconBox: {
      width: 48,
      height: 48,
      borderRadius: Radius.md,
      backgroundColor: palette.secondary,
      justifyContent: 'center',
      alignItems: 'center',
      marginRight: Spacing.sm,
    },
    cardTitle: {
      ...Typography.subtitle,
      color: palette.text,
    },
    summaryBox: {
      backgroundColor: palette.surfaceMuted,
      borderRadius: Radius.md,
      padding: Spacing.md,
    },
    summaryTitle: {
      ...Typography.cardHeading,
      color: palette.text,
      marginBottom: Spacing.sm,
    },
    summaryText: {
      ...Typography.meta,
      fontSize: 14,
      lineHeight: 20,
      color: palette.textSecondary,
    },
    summaryMeta: {
      ...Typography.meta,
      color: palette.textSecondary,
      marginTop: Spacing.sm,
    },
    placeholderBox: {
      backgroundColor: palette.surfaceMuted,
      borderRadius: Radius.md,
      padding: Spacing.lg,
      alignItems: 'center',
      borderWidth: 1,
      borderColor: palette.border,
      borderStyle: 'dashed',
    },
    placeholderText: {
      ...Typography.cardHeading,
      color: palette.textSecondary,
      marginBottom: Spacing.xs,
    },
    placeholderSubtext: {
      ...Typography.meta,
      fontSize: 14,
      color: palette.textSecondary,
      textAlign: 'center',
    },
    placeholderContent: {
      backgroundColor: palette.surfaceMuted,
      borderRadius: Radius.md,
      padding: Spacing.md + 4,
      alignItems: 'center',
    },
    statsContainer: {
      backgroundColor: palette.surfaceMuted,
      borderRadius: Radius.md,
      padding: Spacing.md,
    },
    statRow: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      paddingVertical: Spacing.sm,
      borderBottomWidth: 1,
      borderBottomColor: palette.border,
    },
    statLabel: {
      ...Typography.meta,
      fontSize: 14,
      color: palette.textSecondary,
      textTransform: 'capitalize',
    },
    statValue: {
      ...Typography.meta,
      fontSize: 14,
      fontWeight: '700',
      color: palette.text,
    },
  });
}
