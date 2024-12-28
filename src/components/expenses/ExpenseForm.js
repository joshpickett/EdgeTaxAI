import React, { useState } from 'react';
import { View, TextInput, StyleSheet } from 'react-native';
import { setupSrcPath } from '../../setup_path';
import CustomButton from '../CustomButton';
import { colors, typography, spacing } from '../../styles/tokens';

const ExpenseForm = ({ onSubmit }) => {
  const [description, setDescription] = useState('');
  const [amount, setAmount] = useState('');
  const [date, setDate] = useState('');

  const handleSubmit = () => {
    onSubmit({ description, amount, date });
    setDescription('');
    setAmount('');
    setDate('');
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
        placeholder="Date"
        value={date}
        onChangeText={setDate}
      />
      <CustomButton title="Add Expense" onPress={handleSubmit} />
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
    padding: spacing.sm,
    marginBottom: 10,
  }
});

// ...rest of the code...
