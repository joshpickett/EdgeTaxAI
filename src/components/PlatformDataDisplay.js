import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { setupSrcPath } from '../setup_path';
setupSrcPath();
import ErrorMessage from './ErrorMessage';
import LoadingState from './LoadingState';
import { colors, typography, spacing } from '../styles/tokens';

const PlatformDataDisplay = ({ data, loading, error }) => {
  if (loading) {
    return <LoadingState />;
  }

  if (error) {
    return <ErrorMessage message={error} />;
  }

  return (
    <View style={styles.container}>
      {data.map((platform) => (
        <View key={platform.id} style={styles.platformSection}>
          <Text style={styles.platformTitle}>{platform.name}</Text>
          {/* Additional platform details can go here */}
        </View>
      ))}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: spacing.md,
    backgroundColor: colors.background.default,
    borderRadius: spacing.sm,
  },
  platformSection: {
    marginBottom: spacing.md,
  },
  platformTitle: {
    fontSize: typography.fontSize.lg,
    fontWeight: typography.fontWeight.bold,
    marginBottom: spacing.sm,
  }
});

export default PlatformDataDisplay;
