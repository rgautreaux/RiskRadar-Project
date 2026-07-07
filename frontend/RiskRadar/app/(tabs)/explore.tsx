import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Animated,
  ImageSourcePropType,
  ScrollView,
  SafeAreaView,
  View,
  StyleSheet,
  ActivityIndicator,
  RefreshControl,
  TouchableOpacity,
  Text,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';


import { ThemedText } from '@/components/themed-text';
import { Colors, Spacing, Radius, Shadows } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { apiFetch } from '@/utils/api';
import { useAuth } from '@/contexts/auth-context';
import { useCurrentLocation } from '@/contexts/location-context';
import { RiskCard } from '@/components/risk-card';
import { SectionHeader } from '@/components/section-header';
import { HazardChip } from '@/components/hazard-chip';

// ---------------------------------------------------------------------------
// AnimatedAlertCard — isolated component so hooks are called at the top level
// ---------------------------------------------------------------------------
interface AnimatedAlertCardProps {
  alert: AlertItem;
  index: number;
  iconSource: ImageSourcePropType;
  getSeverityLevel: (severity: string) => 'low' | 'moderate' | 'high' | 'critical';
}

function AnimatedAlertCard({ alert, index, iconSource, getSeverityLevel }: AnimatedAlertCardProps) {
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const slideAnim = useRef(new Animated.Value(20)).current;

  useEffect(() => {
    Animated.timing(fadeAnim, {
      toValue: 1,
      duration: 220,
      delay: 80 + index * 60,
      useNativeDriver: true,
    }).start();
    Animated.timing(slideAnim, {
      toValue: 0,
      duration: 220,
      delay: 80 + index * 60,
      useNativeDriver: true,
    }).start();
  }, [fadeAnim, slideAnim, index]);

  const formatTime = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHrs = Math.floor(diffMins / 60);
    if (diffHrs < 24) return `${diffHrs}h ago`;
    const diffDays = Math.floor(diffHrs / 24);
    return `${diffDays}d ago`;
  };

  return (
    <Animated.View
      style={{
        opacity: fadeAnim,
        transform: [{ translateY: slideAnim }],
        marginBottom: Spacing.sm,
      }}
    >
      <RiskCard
        riskType={alert.alert_type}
        title={alert.title}
        severity={getSeverityLevel(alert.severity)}
        iconSource={iconSource}
        description={alert.description ?? `${alert.alert_type} alert from ${alert.source}`}
        value={undefined}
        unit={undefined}
        onPress={undefined}
        meta={formatTime(alert.fetched_at || alert.created_at)}
      />
    </Animated.View>
  );
}
// Map alert_type or hazard type to icon asset
const hazardIconMap: Record<string, ImageSourcePropType> = {
  weather: require('@/assets/icons/hazards/RiskRadar_Weather_Icon.png'),
  'air quality': require('@/assets/icons/hazards/RiskRadar_AirQuality_Icon.png'),
  airquality: require('@/assets/icons/hazards/RiskRadar_AirQuality_Icon.png'),
  pollen: require('@/assets/icons/hazards/RiskRadar_Pollen_Icon.png'),
  pollution: require('@/assets/icons/hazards/RiskRadar_Pollution_Icon.png'),
  earthquake: require('@/assets/icons/hazards/RiskRadar_LocalEQ_Icon.png'),
  flood: require('@/assets/icons/hazards/RiskRadar_LocalFlood_Icon.png'),
  wind: require('@/assets/icons/hazards/RiskRadar_LocalWindEvent_Icon.png'),
  fire: require('@/assets/icons/hazards/RiskRadar_LocalFIre_Icon.png'),
  // fallback
  default: require('@/assets/icons/hazards/RiskRadar_Weather_Icon.png'),
};

interface AlertItem {
  id: number;
  source: string;
  alert_type: string;
  severity: string;
  title: string;
  description: string | null;
  location_name: string | null;
  fetched_at: string;
  created_at: string;
}

export default function AlertsScreen() {
  const scheme = useColorScheme() ?? 'light';
  const palette = Colors[scheme];
  const router = useRouter();
  const { user } = useAuth();
  const { currentLocation } = useCurrentLocation();
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeFilter, setActiveFilter] = useState<string | null>(null);

  // Resolve which zip to use: shared (searched) location > user home > fallback
  const resolvedZip = currentLocation?.zipCode ?? user?.zip_code ?? null;
  const resolvedCity = currentLocation
    ? `${currentLocation.city}, ${currentLocation.state}`
    : null;

  const toggleFilter = (type: string) => {
    setActiveFilter(prev => prev === type ? null : type);
  };

  const fetchAlerts = useCallback(async () => {
    try {
      setError(null);

      // Prefer location-specific alerts when we have a zip code
      if (resolvedZip) {
        const data = await apiFetch<AlertItem[]>(`/location/alerts?zip_code=${resolvedZip}`);
        setAlerts(data);
      } else {
        // No location at all — fall back to global latest alerts
        const data = await apiFetch<AlertItem[]>('/alerts/?limit=50');
        setAlerts(data);
      }
    } catch {
      setError('Could not load alerts. Is the backend running?');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [resolvedZip]);

  useEffect(() => {
    fetchAlerts();
  }, [fetchAlerts]);

  const onRefresh = () => {
    setRefreshing(true);
    fetchAlerts();
  };


  const getSeverityLevel = (severity: string): 'low' | 'moderate' | 'high' | 'critical' => {
    switch (severity.toLowerCase()) {
      case 'critical':
      case 'extreme':
      case 'hazardous':
        return 'critical';
      case 'warning':
      case 'severe':
      case 'unhealthy':
        return 'high';
      case 'moderate':
        return 'moderate';
      case 'low':
      case 'info':
      default:
        return 'low';
    }
  };

  if (loading) {
    return (
      <SafeAreaView style={[styles.safeArea, { backgroundColor: palette.background }]}>
        <View style={[styles.container, styles.centered]}>
          <ActivityIndicator size="large" color={palette.primary} />
          <ThemedText type="body" style={{ marginTop: Spacing.md }}>
            Loading alerts{resolvedCity ? ` for ${resolvedCity}` : ''}…
          </ThemedText>
        </View>
      </SafeAreaView>
    );
  }


  const hazardChips = [
    { hazardType: 'weather', label: 'Weather', icon: hazardIconMap.weather },
    { hazardType: 'airquality', label: 'Air Quality', icon: hazardIconMap.airquality },
    { hazardType: 'pollen', label: 'Pollen', icon: hazardIconMap.pollen },
    { hazardType: 'pollution', label: 'Pollution', icon: hazardIconMap.pollution },
    { hazardType: 'earthquake', label: 'Earthquake', icon: hazardIconMap.earthquake },
    { hazardType: 'flood', label: 'Flood', icon: hazardIconMap.flood },
    { hazardType: 'wind', label: 'Wind', icon: hazardIconMap.wind },
    { hazardType: 'fire', label: 'Fire', icon: hazardIconMap.fire },
  ];

  const filteredAlerts = activeFilter
    ? alerts.filter(alert => {
        const typeKey = (alert.alert_type || '').toLowerCase().replace(/[^a-z]/g, '');
        return typeKey === activeFilter || typeKey.includes(activeFilter) || activeFilter.includes(typeKey);
      })
    : alerts;

  return (
    <SafeAreaView style={[styles.safeArea, { backgroundColor: palette.background }]}>
      {/* Branded Section Header */}
      <SectionHeader
        title="Alerts"
        subtitle={`${filteredAlerts.length} active alert${filteredAlerts.length !== 1 ? 's' : ''}${activeFilter ? ` · filtered` : ''}`}
        style={styles.sectionHeader}
      />

      {/* Location pill — shows which city these alerts are for */}
      <TouchableOpacity
        style={[styles.locationPill, { backgroundColor: palette.surfaceMuted, borderColor: palette.border }]}
        onPress={() => router.push('/(tabs)')}
        activeOpacity={0.7}
        accessibilityRole="button"
        accessibilityLabel={
          resolvedCity
            ? `Alerts for ${resolvedCity}. Tap to change location.`
            : 'No location selected. Tap to choose a location.'
        }
      >
        <Ionicons name="location" size={14} color={palette.primary} />
        <Text style={[styles.locationPillText, { color: palette.text }]} numberOfLines={1}>
          {resolvedCity ?? 'Search a city on Home to filter alerts'}
        </Text>
        <Ionicons name="chevron-forward" size={14} color={palette.textSecondary} />
      </TouchableOpacity>

      {/* Hazard Chips Row */}
      <View style={styles.chipsWrapper}>
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.hazardChipsRow}
        >
          {hazardChips.map((chip) => (
            <HazardChip
              key={chip.hazardType}
              hazardType={chip.hazardType}
              label={chip.label}
              iconSource={chip.icon}
              isActive={activeFilter === chip.hazardType}
              onPress={() => toggleFilter(chip.hazardType)}
              style={{ marginRight: Spacing.sm }}
            />
          ))}
        </ScrollView>
      </View>

      {/* Alerts List */}
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.contentContainer}
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={palette.primary} />
        }
      >
        {error ? (
          <View style={styles.emptyContainer}>
            <ThemedText type="sectionTitle" style={styles.emptyTitle}>
              Connection Error
            </ThemedText>
            <ThemedText
              type="body"
              lightColor={palette.textSecondary}
              darkColor={palette.textSecondary}
              style={styles.emptySubtitle}
            >
              {error}
            </ThemedText>
            <View style={[styles.retryButton, { backgroundColor: palette.primary }]}
            >
              <ThemedText type="cardTitle" lightColor={palette.white} darkColor={palette.white} onPress={fetchAlerts}>
                Retry
              </ThemedText>
            </View>
          </View>
        ) : filteredAlerts.length > 0 ? (
          <View style={styles.alertsContainer}>
            {filteredAlerts.map((alert, i) => {
              // Map alert_type to icon asset
              const typeKey = (alert.alert_type || '').toLowerCase().replace(/[^a-z]/g, '');
              const iconSource =
                hazardIconMap[typeKey] ||
                hazardIconMap[alert.alert_type?.toLowerCase()] ||
                hazardIconMap.default;
              return (
                <AnimatedAlertCard
                  key={alert.id}
                  alert={alert}
                  index={i}
                  iconSource={iconSource}
                  getSeverityLevel={getSeverityLevel}
                />
              );
            })}
          </View>
        ) : (
          <View style={styles.emptyContainer}>
            <ThemedText type="sectionTitle" style={styles.emptyTitle}>
              No Active Alerts
            </ThemedText>
            <ThemedText
              type="body"
              lightColor={palette.textSecondary}
              darkColor={palette.textSecondary}
              style={styles.emptySubtitle}
            >
              You&apos;re all set! Pull down to refresh.
            </ThemedText>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}



const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
  },
  container: {
    flex: 1,
  },
  centered: {
    justifyContent: 'center',
    alignItems: 'center',
  },
  sectionHeader: {
    paddingBottom: 0,
    paddingTop: Spacing.sm,
  },
  locationPill: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    alignSelf: 'flex-start',
    marginHorizontal: Spacing.lg,
    marginTop: Spacing.xs,
    marginBottom: Spacing.sm,
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 999,
    borderWidth: 1,
    maxWidth: '80%',
  },
  locationPillText: {
    fontSize: 13,
    fontWeight: '600',
    flexShrink: 1,
  },
  chipsWrapper: {
    // Fixed height stops the horizontal ScrollView from flex-stretching vertically,
    // which was creating the big empty gap before the alert list.
    height: 56,
    marginBottom: Spacing.xs,
  },
  hazardChipsRow: {
    paddingHorizontal: Spacing.md,
    flexDirection: 'row',
    alignItems: 'center',
  },
  scrollView: {
    flex: 1,
  },
  contentContainer: {
    paddingHorizontal: Spacing.md,
    paddingTop: Spacing.xs,
    paddingBottom: Spacing.xl,
  },
  alertsContainer: {
    gap: Spacing.md,
  },
  alertCard: {
    borderLeftWidth: 4,
    borderRadius: Radius.md,
    padding: Spacing.md,
    ...Shadows.card,
    marginBottom: Spacing.sm,
  },
  alertCardContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  alertLeft: {
    flex: 1,
    flexDirection: 'row',
    gap: Spacing.md,
  },
  alertTextContent: {
    flex: 1,
    justifyContent: 'flex-start',
  },
  alertSeverity: {
    marginTop: Spacing.xs,
    marginBottom: Spacing.xs,
  },
  alertDescription: {
    marginTop: Spacing.xs,
  },
  iconBackground: {
    width: 48,
    height: 48,
    borderRadius: Radius.md,
    justifyContent: 'center',
    alignItems: 'center',
  },
  iconPlaceholder: {
    width: 24,
    height: 24,
    borderRadius: Radius.sm,
  },
  alertRight: {
    justifyContent: 'flex-start',
    marginLeft: Spacing.sm,
  },
  alertTimestamp: {
    textAlign: 'right',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: Spacing.xl,
  },
  emptyTitle: {
    marginBottom: Spacing.sm,
  },
  emptySubtitle: {
    textAlign: 'center',
  },
  retryButton: {
    marginTop: Spacing.lg,
    paddingVertical: Spacing.sm,
    paddingHorizontal: Spacing.lg,
    borderRadius: Radius.button,
  },
});
