import React, { useState } from 'react';
import { View, TextInput, StyleSheet, Alert } from 'react-native';
import { useDispatch } from 'react-redux';
import CustomButton from '../CustomButton';
import { addExpense } from '../../store/slices/expenseSlice';
import { throwIf } from '../../utils/errorHandler';
import { colors, spacing, typography } from '../../styles/tokens';

const ExpenseForm = ({ onSubmit }) => {
  const [description, setDescription] = useState('');
  const [amount, setAmount] = useState('');
  const [category, setCategory] = useState('');
  const dispatch = useDispatch();

  const validateForm = () => {
    throwIf(!description.trim(), 'Description is required');
    throwIf(!amount.trim(), 'Amount is required');
    throwIf(isNaN(parseFloat(amount)), 'Amount must be a valid number');
    throwIf(parseFloat(amount) <= 0, 'Amount must be greater than 0');
  };

  const handleSubmit = async () => {
    try {
      validateForm();
      
      const expenseData = {
        description: description.trim(),
        amount: parseFloat(amount),
        category: category.trim() || 'Uncategorized',
        date: new Date().toISOString()
      };

      await dispatch(addExpense(expenseData)).unwrap();
      onSubmit?.(expenseData);
      resetForm();
    } catch (error) {
      Alert.alert('Error', error.message);
    }
  };

  const resetForm = () => {
    setDescription('');
    setAmount('');
    setCategory('');
  };

  return (
    <View style={styles.container}>
      <TextInput
        style={styles.input}
        placeholder="Description"
        value={description}
        onChangeText={setDescription}
      />
      <TextInput
        style={styles.input}
        placeholder="Amount"
        value={amount}
        onChangeText={setAmount}
        keyboardType="numeric"
      />
      <TextInput
        style={styles.input}
        placeholder="Category (optional)"
        value={category}
        onChangeText={setCategory}
      />
      <CustomButton 
        title="Add Expense"
        onPress={handleSubmit}
        style={styles.button}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: spacing.md,
  },
  input: {
    borderWidth: 1,
    borderColor: colors.grey[300],
    borderRadius: 8,
    padding: spacing.sm,
    marginBottom: spacing.md,
    fontSize: typography.fontSize.md,
  },
  button: {
    marginTop: spacing.sm,
  },
});

export default ExpenseForm;
