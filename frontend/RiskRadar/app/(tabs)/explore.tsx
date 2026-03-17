import React, { useState } from 'react';
import {
  ScrollView,
  View,
  StyleSheet,
  TouchableOpacity,
  Image,
  Platform,
} from 'react-native';

import { ThemedView } from '@/components/themed-view';
import { ThemedText } from '@/components/themed-text';
import { Colors, Spacing, Radius, Shadows } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';

interface AlertItem {
  id: string;
  title: string;
  description: string;
  severity: 'critical' | 'warning' | 'info';
  timestamp: string;
  icon: string;
  type: string;
}

/**
 * Placeholder alert data for wireframe-accurate list.
 * In production, this would be fetched from the backend API.
 */
const PLACEHOLDER_ALERTS: AlertItem[] = [
  {
    id: '1',
    title: 'Air Quality Alert',
    description: 'Unhealthy air quality detected in your area',
    severity: 'critical',
    timestamp: '2 hours ago',
    icon: 'AirQuality',
    type: 'Air Quality',
  },
  {
    id: '2',
    title: 'Fire Weather Warning',
    description: 'High fire weather conditions expected',
    severity: 'warning',
    timestamp: '1 hour ago',
    icon: 'Fire',
    type: 'Fire',
  },
  {
    id: '3',
    title: 'Pollen Count Elevated',
    description: 'High pollen levels today, may affect allergies',
    severity: 'info',
    timestamp: '30 minutes ago',
    icon: 'Pollen',
    type: 'Pollen',
  },
];

export default function AlertsScreen() {
  const scheme = useColorScheme() ?? 'light';
  const palette = Colors[scheme];
  const [alerts] = useState<AlertItem[]>(PLACEHOLDER_ALERTS);

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return palette.danger;
      case 'warning':
        return palette.warning;
      case 'info':
      default:
        return palette.primary;
    }
  };

  return (
    <ThemedView style={styles.container}>
      {/* Header Section */}
      <View style={styles.header}>
        <ThemedText type="title" style={styles.headerTitle}>
          Alerts
        </ThemedText>
        <ThemedText type="body" lightColor={palette.textSecondary} darkColor={palette.textSecondary}>
          {alerts.length} active alert{alerts.length !== 1 ? 's' : ''}
        </ThemedText>
      </View>

      {/* Alerts List */}
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.contentContainer}
        showsVerticalScrollIndicator={false}
      >
        {alerts.length > 0 ? (
          <View style={styles.alertsContainer}>
            {alerts.map((alert) => (
              <AlertCard
                key={alert.id}
                alert={alert}
                severityColor={getSeverityColor(alert.severity)}
                palette={palette}
              />
            ))}
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
              You're all set! Check back later for updates.
            </ThemedText>
          </View>
        )}
      </ScrollView>
    </ThemedView>
  );
}

/**
 * AlertCard displays a single alert item with wireframe-accurate styling.
 */
function AlertCard({
  alert,
  severityColor,
  palette,
}: {
  alert: AlertItem;
  severityColor: string;
  palette: typeof Colors.light;
}) {
  return (
    <TouchableOpacity
      style={[
        styles.alertCard,
        { backgroundColor: palette.card, borderLeftColor: severityColor },
      ]}
      activeOpacity={0.7}
    >
      <View style={styles.alertCardContent}>
        {/* Left: Icon & Title */}
        <View style={styles.alertLeft}>
          {/* Icon Background */}
          <View
            style={[
              styles.iconBackground,
              { backgroundColor: severityColor, opacity: 0.15 },
            ]}
          >
            <View
              style={[
                styles.iconPlaceholder,
                { backgroundColor: severityColor },
              ]}
            />
          </View>

          {/* Text Content */}
          <View style={styles.alertTextContent}>
            <ThemedText type="cardTitle" numberOfLines={1}>
              {alert.type}
            </ThemedText>
            <ThemedText
              type="eyebrow"
              lightColor={severityColor}
              darkColor={severityColor}
              numberOfLines={1}
              style={styles.alertSeverity}
            >
              {alert.severity.toUpperCase()}
            </ThemedText>
            <ThemedText
              type="meta"
              lightColor={palette.textSecondary}
              darkColor={palette.textSecondary}
              numberOfLines={2}
              style={styles.alertDescription}
            >
              {alert.description}
            </ThemedText>
          </View>
        </View>

        {/* Right: Timestamp */}
        <View style={styles.alertRight}>
          <ThemedText
            type="meta"
            lightColor={palette.textSecondary}
            darkColor={palette.textSecondary}
            style={styles.alertTimestamp}
          >
            {alert.timestamp}
          </ThemedText>
        </View>
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    paddingHorizontal: Spacing.md,
    paddingTop: Spacing.lg,
    paddingBottom: Spacing.sm,
  },
  headerTitle: {
    marginBottom: Spacing.xs,
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
});
