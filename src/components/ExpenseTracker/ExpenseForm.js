import React, { useState } from 'react';
import { View, StyleSheet } from 'react-native';
import { setupSrcPath } from '../../setup_path';
import InputField from '../InputField';
import { colors, spacing, typography } from '../../styles/tokens';

const ExpenseForm = () => {
  const [description, setDescription] = useState('');
  const [amount, setAmount] = useState('');

  const handleAddExpense = () => {
    // Logic to add expense
  };

  return (
    <View style={styles.container}>
      <InputField
        label="Description"
        value={description}
        onChangeText={setDescription}
      />
      <InputField
        label="Amount"
        value={amount}
        onChangeText={setAmount}
      />
      {/* Add Button */}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: spacing.lg,
    width: '100%',
  },
  button: {
    marginTop: spacing.lg,
    backgroundColor: colors.primary.main,
  }
});

export default ExpenseForm;
