import React, { useState } from "react";
import {
  View,
  Text,
  TextInput,
  Button,
  StyleSheet,
  Alert,
  TouchableOpacity,
} from "react-native";
import * as DocumentPicker from "expo-document-picker";
import { addExpense } from "../services/expenseService"; // Unified expense service

const AddExpenseScreen = ({ navigation }) => {
  const [description, setDescription] = useState("");
  const [amount, setAmount] = useState("");
  const [category, setCategory] = useState("");
  const [date, setDate] = useState("");
  const [receipt, setReceipt] = useState(null);

  // Handle Receipt Upload
  const pickDocument = async () => {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: "*/*", // Allow all file types
        copyToCacheDirectory: true,
      });

      if (result.type === "success") {
        setReceipt(result);
        Alert.alert("Success", "Receipt selected successfully.");
      }
    } catch (error) {
      console.error("Error picking receipt:", error.message);
      Alert.alert("Error", "Failed to select receipt.");
    }
  };

  // Handle Add Expense
  const handleAddExpense = async () => {
    if (!description || !amount || !category || !date) {
      Alert.alert("Error", "Please fill in all required fields.");
      return;
    }

    try {
      // Call the addExpense API with receipt (optional)
      await addExpense(description, amount, category, date, receipt);
      Alert.alert("Success", "Expense added successfully!");
      navigation.goBack(); // Navigate back after success
    } catch (error) {
      console.error("Error adding expense:", error.message);
      Alert.alert("Error", "Failed to add expense. Please try again.");
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Add New Expense</Text>

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
        keyboardType="numeric"
        onChangeText={setAmount}
      />
      <TextInput
        style={styles.input}
        placeholder="Category"
        value={category}
        onChangeText={setCategory}
      />
      <TextInput
        style={styles.input}
        placeholder="Date (YYYY-MM-DD)"
        value={date}
        onChangeText={setDate}
      />

      <TouchableOpacity style={styles.uploadButton} onPress={pickDocument}>
        <Text style={styles.buttonText}>
          {receipt ? "Receipt Selected" : "Upload Receipt (Optional)"}
        </Text>
      </TouchableOpacity>

      <Button title="Add Expense" onPress={handleAddExpense} color="#007BFF" />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: "#f9f9f9",
  },
  title: {
    fontSize: 22,
    fontWeight: "bold",
    marginBottom: 20,
    textAlign: "center",
  },
  input: {
    borderWidth: 1,
    borderColor: "#ccc",
    padding: 10,
    marginBottom: 10,
    borderRadius: 5,
    backgroundColor: "#fff",
  },
  uploadButton: {
    backgroundColor: "#28a745",
    padding: 10,
    borderRadius: 5,
    marginBottom: 20,
    alignItems: "center",
  },
  buttonText: {
    color: "#fff",
    fontWeight: "bold",
  },
});

export default AddExpenseScreen;
