import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Animated, ImageSourcePropType } from 'react-native';

import {
  ScrollView,
  View,
  StyleSheet,
  ActivityIndicator,
  RefreshControl,
} from 'react-native';


import { ThemedView } from '@/components/themed-view';
import { ThemedText } from '@/components/themed-text';
import { Colors, Spacing, Radius, Shadows } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { apiFetch } from '@/utils/api';
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
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchAlerts = useCallback(async () => {
    try {
      setError(null);
      const data = await apiFetch<AlertItem[]>('/alerts/?limit=50');
      setAlerts(data);
    } catch (err: any) {
      setError('Could not load alerts. Is the backend running?');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

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

  // const formatTime = (dateStr: string) => {
  //   const date = new Date(dateStr);
  //   const now = new Date();
  //   const diffMs = now.getTime() - date.getTime();
  //   const diffMins = Math.floor(diffMs / 60000);
  //   if (diffMins < 60) return `${diffMins}m ago`;
  //   const diffHrs = Math.floor(diffMins / 60);
  //   if (diffHrs < 24) return `${diffHrs}h ago`;
  //   const diffDays = Math.floor(diffHrs / 24);
  //   return `${diffDays}d ago`;
  // };

  if (loading) {
    return (
      <ThemedView style={[styles.container, styles.centered]}>
        <ActivityIndicator size="large" color={palette.primary} />
        <ThemedText type="body" style={{ marginTop: Spacing.md }}>
          Loading alerts...
        </ThemedText>
      </ThemedView>
    );
  }


  // Example hazard chips (static for now, could be dynamic)
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

  return (
    <ThemedView style={styles.container}>
      {/* Branded Section Header */}
      <SectionHeader
        title="Alerts"
        subtitle={`${alerts.length} active alert${alerts.length !== 1 ? 's' : ''}`}
        style={styles.sectionHeader}
      />

      {/* Hazard Chips Row */}
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.hazardChipsRow}
        style={{ marginBottom: Spacing.md }}
      >
        {hazardChips.map((chip) => (
          <HazardChip
            key={chip.hazardType}
            hazardType={chip.hazardType}
            label={chip.label}
            iconSource={chip.icon}
            isActive={false}
            style={{ marginRight: Spacing.sm }}
          />
        ))}
      </ScrollView>

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
        ) : alerts.length > 0 ? (
          <View style={styles.alertsContainer}>
            {alerts.map((alert, i) => {
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
    </ThemedView>
  );
}



const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  centered: {
    justifyContent: 'center',
    alignItems: 'center',
  },
  sectionHeader: {
    paddingBottom: 0,
  },
  hazardChipsRow: {
    paddingHorizontal: Spacing.md,
    paddingBottom: Spacing.sm,
    flexDirection: 'row',
    alignItems: 'center',
  },
  scrollView: {
    flex: 1,
  },
  contentContainer: {
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.md,
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
