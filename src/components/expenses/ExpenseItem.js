import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { setupSrcPath } from '../../setup_path';
import { formatCurrency, formatDate } from '../../utils/formatting';
import { colors, typography, spacing } from '../../styles/tokens';

const ExpenseItem = ({ expense, onDelete, onEdit }) => {
  return (
    <View style={styles.container}>
      <View>
        <Text>{formatDate(expense.date)}</Text>
        <Text>{expense.description}</Text>
      </View>
      <View>
        <Text>{formatCurrency(expense.amount)}</Text>
        <TouchableOpacity onPress={onEdit}>
          <Text>Edit</Text>
        </TouchableOpacity>
        <TouchableOpacity onPress={onDelete}>
          <Text>Delete</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    padding: spacing.md,
    backgroundColor: colors.background.default,
    borderRadius: spacing.sm,
    marginBottom: 10,
  },
  amount: {
    fontSize: typography.fontSize.md,
    fontWeight: typography.fontWeight.bold,
  }
});

// ...rest of the code...
