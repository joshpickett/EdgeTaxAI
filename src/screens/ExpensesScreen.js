import React, { useState } from "react";
import { View, Text, TextInput, StyleSheet, Alert } from "react-native";
import CustomButton from "../components/CustomButton";
import { validateAmount, validateDescription, validateDate } from "../utils/validation";

const ExpensesScreen = ({ navigation }) => {
  const [description, setDescription] = useState("");
  const [amount, setAmount] = useState("");
  const [errors, setErrors] = useState({});

  const handleAddExpense = async () => {
    // Clear previous errors
    setErrors({});

    // Validate all fields
    const descError = validateDescription(description);
    const amountError = validateAmount(amount);
    
    if (descError || amountError) {
      setErrors({
        description: descError,
        amount: amountError,
      });
      return;
    }

    // Proceed with adding the expense
    // ...rest of the code...
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Add Expense</Text>
      <TextInput
        style={[styles.input, errors.description && styles.inputError]}
        placeholder="Description"
        value={description}
        onChangeText={setDescription}
      />
      {errors.description && <Text style={styles.errorText}>{errors.description}</Text>}
      <TextInput
        style={[styles.input, errors.amount && styles.inputError]}
        placeholder="Amount"
        value={amount}
        onChangeText={setAmount}
        keyboardType="numeric"
      />
      {errors.amount && <Text style={styles.errorText}>{errors.amount}</Text>}
      <CustomButton title="Add Expense" onPress={handleAddExpense} />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: "bold",
    marginBottom: 20,
  },
  input: {
    borderWidth: 1,
    borderColor: '#ccc',
    padding: 10,
    borderRadius: 5,
    marginBottom: 10,
  },
  inputError: {
    borderColor: '#ff0000',
  },
  errorText: {
    color: '#ff0000',
    fontSize: 12,
    marginTop: 5,
  }
});
