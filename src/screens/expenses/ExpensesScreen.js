import React, { useEffect, useState } from "react";
import { View, Text, FlatList, Button, Alert, StyleSheet, TextInput } from "react-native";
import { editExpense, deleteExpense } from "../services/expenseService";

const ExpensesScreen = () => {
  const [expenses, setExpenses] = useState([]);
  const [selectedExpense, setSelectedExpense] = useState(null);
  const [editedExpense, setEditedExpense] = useState({ description: "", amount: "", category: "" });

  useEffect(() => {
    // Load expenses (mock data here)
    setExpenses([
      { id: 1, description: "Lunch", amount: "15.00", category: "Food" },
      { id: 2, description: "Taxi", amount: "20.00", category: "Transport" },
    ]);
  }, []);

  const handleEdit = async (id) => {
    try {
      await editExpense(id, editedExpense);
      Alert.alert("Success", "Expense updated successfully!");
      // Refresh data or filter updated expense
    } catch (error) {
      Alert.alert("Error", "Failed to update expense.");
    }
  };

  const handleDelete = async (id) => {
    try {
      await deleteExpense(id);
      setExpenses(expenses.filter((expense) => expense.id !== id));
      Alert.alert("Success", "Expense deleted successfully!");
    } catch (error) {
      Alert.alert("Error", "Failed to delete expense.");
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Expenses</Text>
      <FlatList
        data={expenses}
        keyExtractor={(item) => item.id.toString()}
        renderItem={({ item }) => (
          <View style={styles.item}>
            <Text>{item.description} - ${item.amount}</Text>
            <Button title="Edit" onPress={() => setSelectedExpense(item)} />
            <Button title="Delete" color="red" onPress={() => handleDelete(item.id)} />
          </View>
        )}
      />
      {selectedExpense && (
        <View style={styles.editor}>
          <TextInput
            style={styles.input}
            placeholder="Description"
            value={editedExpense.description}
            onChangeText={(text) => setEditedExpense({ ...editedExpense, description: text })}
          />
          <TextInput
            style={styles.input}
            placeholder="Amount"
            value={editedExpense.amount}
            onChangeText={(text) => setEditedExpense({ ...editedExpense, amount: text })}
          />
          <TextInput
            style={styles.input}
            placeholder="Category"
            value={editedExpense.category}
            onChangeText={(text) => setEditedExpense({ ...editedExpense, category: text })}
          />
          <Button title="Save Changes" onPress={() => handleEdit(selectedExpense.id)} />
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20 },
  title: { fontSize: 22, fontWeight: "bold", marginBottom: 10 },
  item: { padding: 10, borderBottomWidth: 1, borderColor: "#ccc", flexDirection: "row", justifyContent: "space-between" },
  editor: { padding: 10, borderTopWidth: 1, borderColor: "#ccc" },
  input: { borderWidth: 1, borderColor: "#ddd", marginBottom: 10, padding: 8, borderRadius: 5 },
});

export default ExpensesScreen;
