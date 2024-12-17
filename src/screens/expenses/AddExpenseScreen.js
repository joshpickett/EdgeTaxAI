import React, { useState } from "react";
import { View, Text, StyleSheet, TextInput, Button, Alert } from "react-native";
import * as ImagePicker from "expo-image-picker";
import { addExpense } from "../services/api";

const AddExpenseScreen = ({ navigation }) => {
  const [description, setDescription] = useState("");
  const [amount, setAmount] = useState("");
  const [category, setCategory] = useState("");
  const [date, setDate] = useState(new Date().toISOString().split("T")[0]);
  const [receipt, setReceipt] = useState(null);

  const pickReceipt = async () => {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      quality: 1,
    });
    if (!result.canceled) {
      setReceipt(result.assets[0]);
    }
  };

  const handleAddExpense = async () => {
    try {
      const response = await addExpense(description, amount, category, date, receipt);
      if (response.success) {
        Alert.alert("Success", "Expense added successfully!");
        navigation.goBack();
      } else {
        Alert.alert("Error", response.message || "Failed to add expense.");
      }
    } catch (error) {
      Alert.alert("Error", "Unable to add expense.");
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Add Expense</Text>
      <TextInput placeholder="Description" value={description} onChangeText={setDescription} style={styles.input} />
      <TextInput placeholder="Amount" value={amount} onChangeText={setAmount} keyboardType="numeric" style={styles.input} />
      <TextInput placeholder="Category" value={category} onChangeText={setCategory} style={styles.input} />
      <TextInput placeholder="Date" value={date} onChangeText={setDate} style={styles.input} />
      <Button title="Upload Receipt" onPress={pickReceipt} />
      {receipt && <Text>Receipt: {receipt.fileName}</Text>}
      <Button title="Add Expense" onPress={handleAddExpense} />
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20 },
  title: { fontSize: 24, marginBottom: 20, textAlign: "center" },
  input: { borderWidth: 1, padding: 10, marginVertical: 10, borderRadius: 5 },
});

export default AddExpenseScreen;
