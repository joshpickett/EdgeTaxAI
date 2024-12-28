import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { setupSrcPath } from '../setup_path';
setupSrcPath();
import { VictoryPie } from 'victory-native';
import { formatCurrency } from '../utils/formatting';
import { colors, typography, spacing } from '../styles/tokens';

const TaxSummaryCard = ({ taxData }) => {
  const pieData = [
    // Data processing logic here
  ];

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Tax Summary</Text>
      <VictoryPie data={pieData} />
      {taxData.map((item, index) => (
        <View key={index} style={styles.row}>
          <Text style={styles.label}>{item.label}</Text>
          <Text style={styles.label}>{item.value}</Text>
        </View>
      ))}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: spacing.md,
    backgroundColor: colors.background.default,
    borderRadius: spacing.md,
    elevation: spacing.xs,
  },
  title: {
    fontSize: typography.fontSize.xl,
    fontWeight: typography.fontWeight.bold,
    marginBottom: spacing.md,
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: spacing.sm,
  },
  label: {
    fontSize: typography.fontSize.md,
    color: colors.text.secondary,
  }
});
