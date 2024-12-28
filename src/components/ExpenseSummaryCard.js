import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { setupSrcPath } from '../setup_path';
import { Card } from 'react-native-elements';
import { colors, typography, spacing } from '../styles/tokens';
import { VictoryPie } from 'victory-native';

const ExpenseSummaryCard = ({ data }) => {
  const { expenses, categories, total } = data;

  return (
    <Card containerStyle={styles.container}>
      <Card.Title>Expense Summary</Card.Title>
      <View style={styles.content}>
        <View style={styles.infoContainer}>
          <Text style={styles.label}>Total Expenses:</Text>
          <Text style={styles.amount}>${total}</Text>
          
          <Text style={styles.label}>Top Categories:</Text>
          {categories.slice(0, 3).map((category, index) => (
            <Text key={index} style={styles.categoryText}>
              {category.name}: ${category.amount}
            </Text>
          ))}
        </View>
        
        <View style={styles.chartContainer}>
          <VictoryPie
            data={categories}
            x="name"
            y="amount"
            colorScale="qualitative"
            labels={({ datum }) => `${datum.name}: $${datum.amount}`}
          />
        </View>
      </View>
    </Card>
  );
};

const styles = StyleSheet.create({
  container: {
    borderRadius: spacing.md,
    marginBottom: spacing.md,
    elevation: spacing.xs
  },
  content: {
    flexDirection: 'row',
    justifyContent: 'space-between'
  },
  infoContainer: {
    flex: 1,
    padding: spacing.sm
  },
  chartContainer: {
    flex: 1,
    alignItems: 'center'
  },
  label: {
    fontSize: typography.fontSize.sm,
    color: colors.text.secondary,
    marginBottom: spacing.xs
  },
  amount: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#FF6B6B',
    marginBottom: 10
  },
  categoryText: {
    fontSize: 14,
    color: '#333',
    marginBottom: 5
  }
});

export default ExpenseSummaryCard;
