import React, { useEffect, useState } from "react";
import { View, Text, FlatList, StyleSheet, ActivityIndicator, Alert, Button } from "react-native";
import { listExpenses } from "../services/expenseService"; // Updated import for unified service

const ExpenseDashboardScreen = ({ userId }) => {
  const [expenses, setExpenses] = useState([]);
  const [loading, setLoading] = useState(true);

  // Fetch expenses on screen load
  useEffect(() => {
    fetchExpenses();
  }, []);

  const fetchExpenses = async () => {
    setLoading(true);
    try {
      const data = await listExpenses(userId); // Fetch user-specific expenses
      setExpenses(data || []);
    } catch (error) {
      console.error("Error fetching expenses:", error.message);
      Alert.alert("Error", "Failed to load expenses. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const renderExpenseItem = ({ item }) => (
    <View style={styles.itemContainer}>
      <Text style={styles.itemText}>
        {item.description} - ${item.amount} ({item.category})
      </Text>
      <Text style={styles.dateText}>Date: {item.date}</Text>
    </View>
  );

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Expense Dashboard</Text>

      {loading ? (
        <ActivityIndicator size="large" color="#007BFF" />
      ) : expenses.length > 0 ? (
        <FlatList
          data={expenses}
          keyExtractor={(item) => item.id.toString()}
          renderItem={renderExpenseItem}
          ListFooterComponent={<Button title="Refresh" onPress={fetchExpenses} />}
        />
      ) : (
        <Text style={styles.emptyText}>No expenses found.</Text>
      )}
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
  itemContainer: {
    padding: 15,
    marginBottom: 10,
    backgroundColor: "#e7f3ff",
    borderRadius: 5,
    borderWidth: 1,
    borderColor: "#007BFF",
  },
  itemText: {
    fontSize: 16,
    fontWeight: "500",
    marginBottom: 5,
  },
  dateText: {
    fontSize: 14,
    color: "#555",
  },
  emptyText: {
    fontSize: 18,
    textAlign: "center",
    color: "#777",
  },
});

export default ExpenseDashboardScreen;
