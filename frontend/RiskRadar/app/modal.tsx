import { StatusBar } from 'expo-status-bar';
import {
  Modal,
  View,
  StyleSheet,
  TouchableOpacity,
  SafeAreaView,
  ScrollView,
} from 'react-native';
import { useRouter } from 'expo-router';
import React, { useState } from 'react';

import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { Colors, Spacing, Radius, Shadows } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';

/**
 * ModalScreen presents a branded notification details surface.
 * In production, this would display detailed information about a selected alert.
 */
export default function ModalScreen() {
  const router = useRouter();
  const scheme = useColorScheme() ?? 'light';
  const palette = Colors[scheme];
  const [isVisible, setIsVisible] = useState(true);

  const handleClose = () => {
    setIsVisible(false);
    router.back();
  };

  return (
    <>
      <Modal
        animationType="slide"
        transparent={true}
        visible={isVisible}
        onRequestClose={handleClose}
      >
        <SafeAreaView style={[styles.modalContainer, { backgroundColor: palette.surface }]}>
          {/* Header with Close Button */}
          <View
            style={[
              styles.modalHeader,
              {
                backgroundColor: palette.card,
                borderBottomColor: palette.border,
              },
            ]}
          >
            <ThemedText type="title" style={styles.modalTitle}>
              Alert Details
            </ThemedText>
            <TouchableOpacity
              onPress={handleClose}
              style={[
                styles.closeButton,
                { backgroundColor: palette.surfaceMuted },
              ]}
              activeOpacity={0.7}
            >
              <ThemedText type="meta" lightColor={palette.text} darkColor={palette.text}>
                ✕
              </ThemedText>
            </TouchableOpacity>
          </View>

          {/* Content */}
          <ScrollView
            style={styles.modalContent}
            contentContainerStyle={styles.contentContainer}
            showsVerticalScrollIndicator={false}
          >
            {/* Notification Panel Container */}
            <ThemedView
              surface="card"
              elevated={true}
              padding="lg"
              style={styles.notificationPanel}
            >
              {/* Alert Icon and Title */}
              <View style={styles.alertHeader}>
                <View
                  style={[
                    styles.alertIcon,
                    { backgroundColor: palette.danger, opacity: 0.15 },
                  ]}
                >
                  <View
                    style={[
                      styles.iconIndicator,
                      { backgroundColor: palette.danger },
                    ]}
                  />
                </View>
                <View style={styles.alertTitleContainer}>
                  <ThemedText
                    type="sectionTitle"
                    lightColor={palette.text}
                    darkColor={palette.text}
                  >
                    Air Quality Alert
                  </ThemedText>
                  <ThemedText
                    type="eyebrow"
                    lightColor={palette.danger}
                    darkColor={palette.danger}
                    style={styles.alertSeverity}
                  >
                    CRITICAL
                  </ThemedText>
                </View>
              </View>

              {/* Alert Description */}
              <View style={styles.section}>
                <ThemedText
                  type="cardTitle"
                  lightColor={palette.text}
                  darkColor={palette.text}
                  style={styles.sectionTitle}
                >
                  Description
                </ThemedText>
                <ThemedText
                  type="body"
                  lightColor={palette.textSecondary}
                  darkColor={palette.textSecondary}
                  style={styles.sectionContent}
                >
                  Unhealthy air quality detected in your area. AQI levels are
                  currently at hazardous levels. Consider limiting outdoor
                  activities and wearing protective masks if you must go outside.
                </ThemedText>
              </View>

              {/* Alert Details */}
              <View style={styles.section}>
                <ThemedText
                  type="cardTitle"
                  lightColor={palette.text}
                  darkColor={palette.text}
                  style={styles.sectionTitle}
                >
                  Details
                </ThemedText>
                <View style={styles.detailRow}>
                  <ThemedText
                    type="meta"
                    lightColor={palette.textSecondary}
                    darkColor={palette.textSecondary}
                  >
                    Location:
                  </ThemedText>
                  <ThemedText type="body" style={styles.detailValue}>
                    Current Location
                  </ThemedText>
                </View>
                <View style={styles.detailRow}>
                  <ThemedText
                    type="meta"
                    lightColor={palette.textSecondary}
                    darkColor={palette.textSecondary}
                  >
                    Time:
                  </ThemedText>
                  <ThemedText type="body" style={styles.detailValue}>
                    2 hours ago
                  </ThemedText>
                </View>
                <View style={styles.detailRow}>
                  <ThemedText
                    type="meta"
                    lightColor={palette.textSecondary}
                    darkColor={palette.textSecondary}
                  >
                    Expiration:
                  </ThemedText>
                  <ThemedText type="body" style={styles.detailValue}>
                    Until 6:00 PM
                  </ThemedText>
                </View>
              </View>

              {/* Recommendations */}
              <View style={styles.section}>
                <ThemedText
                  type="cardTitle"
                  lightColor={palette.text}
                  darkColor={palette.text}
                  style={styles.sectionTitle}
                >
                  Recommendations
                </ThemedText>
                <View style={styles.recommendationItem}>
                  <ThemedText
                    type="body"
                    lightColor={palette.text}
                    darkColor={palette.text}
                  >
                    • Limit outdoor activities
                  </ThemedText>
                </View>
                <View style={styles.recommendationItem}>
                  <ThemedText
                    type="body"
                    lightColor={palette.text}
                    darkColor={palette.text}
                  >
                    • Use air filtration indoors
                  </ThemedText>
                </View>
                <View style={styles.recommendationItem}>
                  <ThemedText
                    type="body"
                    lightColor={palette.text}
                    darkColor={palette.text}
                  >
                    • Wear N95 masks outdoors
                  </ThemedText>
                </View>
              </View>
            </ThemedView>

            {/* Action Button */}
            <TouchableOpacity
              style={[
                styles.actionButton,
                { backgroundColor: palette.primary },
              ]}
              onPress={handleClose}
              activeOpacity={0.8}
            >
              <ThemedText
                type="cardTitle"
                lightColor={palette.white}
                darkColor={palette.white}
              >
                Acknowledge
              </ThemedText>
            </TouchableOpacity>
          </ScrollView>
        </SafeAreaView>
      </Modal>

      <StatusBar barStyle="light-content" />
    </>
  );
}

const styles = StyleSheet.create({
  modalContainer: {
    flex: 1,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.md,
    borderBottomWidth: 1,
  },
  modalTitle: {
    flex: 1,
  },
  closeButton: {
    width: 40,
    height: 40,
    borderRadius: Radius.button,
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    flex: 1,
  },
  contentContainer: {
    padding: Spacing.md,
    flexGrow: 1,
  },
  notificationPanel: {
    marginBottom: Spacing.lg,
    borderRadius: Radius.lg,
  },
  alertHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: Spacing.lg,
  },
  alertIcon: {
    width: 56,
    height: 56,
    borderRadius: Radius.md,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: Spacing.md,
  },
  iconIndicator: {
    width: 28,
    height: 28,
    borderRadius: Radius.sm,
  },
  alertTitleContainer: {
    flex: 1,
  },
  alertSeverity: {
    marginTop: Spacing.xs,
  },
  section: {
    marginBottom: Spacing.lg,
    paddingBottom: Spacing.lg,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(0, 0, 0, 0.06)',
  },
  sectionTitle: {
    marginBottom: Spacing.md,
  },
  sectionContent: {
    lineHeight: 22,
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: Spacing.sm,
  },
  detailValue: {
    flex: 1,
    textAlign: 'right',
  },
  recommendationItem: {
    paddingVertical: Spacing.sm,
  },
  actionButton: {
    paddingVertical: Spacing.md,
    paddingHorizontal: Spacing.lg,
    borderRadius: Radius.button,
    alignItems: 'center',
    justifyContent: 'center',
    ...Shadows.card,
  },
});
