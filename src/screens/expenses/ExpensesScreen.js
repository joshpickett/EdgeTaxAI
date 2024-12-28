import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  TextInput,
  Button,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
} from "react-native";
import ExpenseItem from "components/ExpenseItem";
import AddExpenseForm from "components/AddExpenseForm";
import { styles } from "styles/expenses";
import {
  listExpenses,
  editExpense,
  deleteExpense,
} from "../services/expenseService"; // Updated service imports

const ExpensesScreen = ({ userId }) => {
  const [expenses, setExpenses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingExpenseId, setEditingExpenseId] = useState(null);
  const [editedDescription, setEditedDescription] = useState("");
  const [editedAmount, setEditedAmount] = useState("");

  // Fetch expenses on screen load
  useEffect(() => {
    fetchExpenses();
  }, []);

  const fetchExpenses = async () => {
    setLoading(true);
    try {
      const data = await listExpenses(userId); // Fetch expenses for the user
      setExpenses(data || []);
    } catch (error) {
      console.error("Error fetching expenses:", error.message);
      Alert.alert("Error", "Failed to load expenses.");
    } finally {
      setLoading(false);
    }
  };

  // Handle Delete Expense
  const handleDeleteExpense = async (expenseId) => {
    Alert.alert(
      "Confirm Deletion",
      "Are you sure you want to delete this expense?",
      [
        { text: "Cancel", style: "cancel" },
        {
          text: "Delete",
          style: "destructive",
          onPress: async () => {
            try {
              await deleteExpense(expenseId);
              Alert.alert("Success", "Expense deleted successfully.");
              fetchExpenses(); // Refresh list
            } catch (error) {
              console.error("Error deleting expense:", error.message);
              Alert.alert("Error", "Failed to delete expense.");
            }
          },
        },
      ]
    );
  };

  // Handle Edit Expense
  const handleEditExpense = async (expenseId) => {
    if (!editedDescription || !editedAmount) {
      Alert.alert("Error", "Description and amount cannot be empty.");
      return;
    }

    try {
      await editExpense(expenseId, {
        description: editedDescription,
        amount: parseFloat(editedAmount),
      });
      Alert.alert("Success", "Expense updated successfully.");
      setEditingExpenseId(null);
      fetchExpenses(); // Refresh list
    } catch (error) {
      console.error("Error editing expense:", error.message);
      Alert.alert("Error", "Failed to edit expense.");
    }
  };

  // Render Expense Item
  const renderExpenseItem = ({ item }) => (
    <View style={styles.itemContainer}>
      {editingExpenseId === item.id ? (
        // Inline Editing UI
        <>
          <TextInput
            style={styles.input}
            placeholder="Description"
            value={editedDescription}
            onChangeText={setEditedDescription}
          />
          <TextInput
            style={styles.input}
            placeholder="Amount"
            value={editedAmount}
            keyboardType="numeric"
            onChangeText={setEditedAmount}
          />
          <Button
            title="Save"
            onPress={() => handleEditExpense(item.id)}
            color="#28a745"
          />
          <Button
            title="Cancel"
            onPress={() => setEditingExpenseId(null)}
            color="#dc3545"
          />
        </>
      ) : (
        // Read-Only Expense UI
        <>
          <Text style={styles.itemText}>
            {item.description} - ${item.amount} ({item.category})
          </Text>
          <Text style={styles.dateText}>Date: {item.date}</Text>
          <View style={styles.buttonRow}>
            <TouchableOpacity
              style={styles.editButton}
              onPress={() => {
                setEditingExpenseId(item.id);
                setEditedDescription(item.description);
                setEditedAmount(item.amount.toString());
              }}
            >
              <Text style={styles.buttonText}>Edit</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={styles.deleteButton}
              onPress={() => handleDeleteExpense(item.id)}
            >
              <Text style={styles.buttonText}>Delete</Text>
            </TouchableOpacity>
          </View>
        </>
      )}
    </View>
  );

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Your Expenses</Text>

      {loading ? (
        <ActivityIndicator size="large" color="#007BFF" />
      ) : expenses.length > 0 ? (
        <FlatList
          data={expenses}
          keyExtractor={(item) => item.id.toString()}
          renderItem={renderExpenseItem}
          ListFooterComponent={
            <Button title="Refresh" onPress={fetchExpenses} color="#007BFF" />
          }
        />
      ) : (
        <Text style={styles.emptyText}>No expenses found.</Text>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, backgroundColor: "#f9f9f9" },
  title: { fontSize: 22, fontWeight: "bold", marginBottom: 20, textAlign: "center" },
  itemContainer: {
    backgroundColor: "#e7f3ff",
    padding: 15,
    marginBottom: 10,
    borderRadius: 5,
    borderColor: "#007BFF",
    borderWidth: 1,
  },
  itemText: { fontSize: 16, fontWeight: "500" },
  dateText: { fontSize: 14, color: "#555", marginBottom: 5 },
  buttonRow: { flexDirection: "row", justifyContent: "space-between" },
  editButton: { backgroundColor: "#ffc107", padding: 10, borderRadius: 5 },
  deleteButton: { backgroundColor: "#dc3545", padding: 10, borderRadius: 5 },
  buttonText: { color: "#fff", textAlign: "center", fontWeight: "600" },
  input: {
    borderWidth: 1,
    borderColor: "#ccc",
    padding: 10,
    marginBottom: 10,
    borderRadius: 5,
  },
  emptyText: { textAlign: "center", fontSize: 18, color: "#777" },
});

export default ExpensesScreen;
