import React, { useState, useEffect } from "react";
import { View, Text, TextInput, Button, FlatList, StyleSheet, Alert, ScrollView } from "react-native";
import { getTaxSavings, getDeductionSuggestions } from "../services/taxService";

const TaxOptimizationScreen = () => {
  const [amount, setAmount] = useState("");
  const [taxRate, setTaxRate] = useState(null);
  const [taxSavings, setTaxSavings] = useState(null);
  const [deductions, setDeductions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const [savings, setSavings] = useState(null);

  // Fetch the tax rate when the screen loads
  useEffect(() => {
    const fetchTaxRate = async () => {
      try {
        const rate = await getTaxRate(); // Fetches from /api/config
        setTaxRate(rate);
      } catch (error) {
        Alert.alert("Error", "Failed to fetch tax rate.");
      }
    };

    fetchTaxRate();
  }, []);

  const handleCalculateSavings = async () => {
    if (!amount) {
      Alert.alert("Error", "Please enter an amount.");
      return;
    }

    try {
      const result = await getTaxSavings(amount);
      setTaxSavings(result);
      
      // Get AI-powered suggestions
      const deductionSuggestions = await getDeductionSuggestions({
        amount,
        category: selectedCategory
      });
      setSuggestions(deductionSuggestions);
    } catch (error) {
      console.error("Error:", error);
    }
  };

  const handleFetchDeductions = async () => {
    try {
      const expenses = [{ description: "Sample Expense", amount }];
      const result = await getDeductionSuggestions(expenses);
      setDeductions(result);
    } catch (error) {
      Alert.alert("Error", "Failed to fetch deduction suggestions.");
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Tax Optimization</Text>

      {taxRate !== null ? (
        <Text style={styles.taxRate}>Current Tax Rate: {taxRate * 100}%</Text>
      ) : (
        <Text style={styles.taxRate}>Fetching tax rate...</Text>
      )}

      <TextInput
        style={styles.input}
        placeholder="Enter expense amount"
        keyboardType="numeric"
        value={amount}
        onChangeText={setAmount}
      />

      <Button title="Calculate Tax Savings" onPress={handleCalculateSavings} />
      {taxSavings !== null && (
        <Text style={styles.result}>Estimated Tax Savings: ${taxSavings.toFixed(2)}</Text>
      )}

      <Button title="Fetch Deduction Suggestions" onPress={handleFetchDeductions} />
      <FlatList
        data={deductions}
        keyExtractor={(item, index) => index.toString()}
        renderItem={({ item }) => (
          <Text style={styles.item}>{item.description || "Unnamed Expense"}: ${item.amount}</Text>
        )}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, backgroundColor: "#f9f9f9" },
  title: { fontSize: 22, fontWeight: "bold", marginBottom: 20, textAlign: "center" },
  taxRate: { fontSize: 16, marginBottom: 10, textAlign: "center" },
  input: { borderWidth: 1, borderColor: "#ccc", padding: 10, borderRadius: 5, marginBottom: 20 },
  result: { marginTop: 20, fontSize: 18, color: "green", textAlign: "center" },
  item: { padding: 10, borderBottomWidth: 1, borderColor: "#ddd" },
});

export default TaxOptimizationScreen;
