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
import { addExpense, categorizeExpense } from "../services/expenseService";

const BASE_URL = "https://your-backend-api.com/api/ocr/receipt"; // Replace with your OCR endpoint

const AddExpenseScreen = ({ navigation }) => {
  const [description, setDescription] = useState("");
  const [amount, setAmount] = useState("");
  const [category, setCategory] = useState("");
  const [date, setDate] = useState("");
  const [receipt, setReceipt] = useState(null);

  // Auto-Categorize Expense
  const handleAutoCategorize = async () => {
    if (!description.trim()) {
      Alert.alert("Error", "Please enter a description to categorize.");
      return;
    }
    try {
      const predictedCategory = await categorizeExpense(description);
      setCategory(predictedCategory);
      Alert.alert("Category Suggested", `Category: ${predictedCategory}`);
    } catch (error) {
      console.error("Categorization Error:", error.message);
      Alert.alert("Error", "Failed to auto-categorize expense. Please try again.");
    }
  };

  // Handle Add Expense
  const handleAddExpense = async () => {
    if (!description || !amount || !category || !date) {
      Alert.alert("Error", "Please fill in all fields.");
      return;
    }

    try {
      await addExpense(description, amount, category, date);
      Alert.alert("Success", "Expense added successfully!");
      navigation.goBack();
    } catch (error) {
      console.error("Add Expense Error:", error.message);
      Alert.alert("Error", "Failed to add expense. Please try again.");
    }
  };

  // Upload Receipt and Process OCR
  const handleReceiptUpload = async () => {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: "image/*",
        copyToCacheDirectory: true,
      });

      if (result.type === "success") {
        setReceipt(result); // Save receipt file state
        await processReceiptOCR(result.uri);
      }
    } catch (error) {
      console.error("Receipt Upload Error:", error.message);
      Alert.alert("Error", "Failed to upload receipt. Please try again.");
    }
  };

  const processReceiptOCR = async (uri) => {
    try {
      const formData = new FormData();
      formData.append("receipt", {
        uri,
        type: "image/jpeg",
        name: "receipt.jpg",
      });

      const response = await fetch(BASE_URL, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      if (response.ok) {
        setDescription(data.text); // Set extracted text as the description
        Alert.alert("Receipt Processed", "Text extracted from the receipt.");
      } else {
        Alert.alert("Error", data.error || "Failed to process receipt.");
      }
    } catch (error) {
      console.error("OCR Processing Error:", error.message);
      Alert.alert("Error", "Failed to process receipt. Please try again.");
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Add New Expense</Text>

      {/* Description Input */}
      <TextInput
        style={styles.input}
        placeholder="Description"
        value={description}
        onChangeText={setDescription}
        onBlur={handleAutoCategorize} // Auto-categorize when description input loses focus
      />

      {/* Amount Input */}
      <TextInput
        style={styles.input}
        placeholder="Amount"
        value={amount}
        keyboardType="numeric"
        onChangeText={setAmount}
      />

      {/* Category Input */}
      <TextInput
        style={styles.input}
        placeholder="Category"
        value={category}
        onChangeText={setCategory}
      />

      {/* Date Input */}
      <TextInput
        style={styles.input}
        placeholder="Date (YYYY-MM-DD)"
        value={date}
        onChangeText={setDate}
      />

      {/* Receipt Upload */}
      <TouchableOpacity style={styles.uploadButton} onPress={handleReceiptUpload}>
        <Text style={styles.buttonText}>
          {receipt ? "Receipt Uploaded" : "Upload Receipt"}
        </Text>
      </TouchableOpacity>

      {/* Submit Button */}
      <Button title="Add Expense" onPress={handleAddExpense} color="#007BFF" />
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, backgroundColor: "#f9f9f9" },
  title: {
    fontSize: 22,
    fontWeight: "bold",
    textAlign: "center",
    marginVertical: 10,
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
  buttonText: { color: "#fff", fontWeight: "bold" },
});

export default AddExpenseScreen;
