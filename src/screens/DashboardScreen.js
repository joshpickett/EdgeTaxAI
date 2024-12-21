import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  ActivityIndicator,
  FlatList,
  Button,
  Alert,
  TextInput,
} from "react-native";
import { VictoryPie, VictoryBar, VictoryChart, VictoryTheme } from "victory-native";
import { fetchExpenseReports, editExpense, deleteExpense } from "../services/reportsService";

const DashboardScreen = ({ onLogout }) => {
  const [expenseData, setExpenseData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expensesList, setExpensesList] = useState([]); // Detailed expense list for FlatList
  const [editMode, setEditMode] = useState(null); // Tracks editing expense ID
  const [editedValues, setEditedValues] = useState({}); // Edited values for an expense

  // Load expense data on component mount
  useEffect(() => {
    loadExpenseData();
  }, []);

  const loadExpenseData = async () => {
    setLoading(true);
    try {
      const data = await fetchExpenseReports();

      // Format data for Victory Charts
      const formattedData = data.reports.map((item) => ({
        x: item.category, // X-axis: Category name
        y: item.amount,   // Y-axis: Expense amount
      }));

      // Set detailed expenses for FlatList
      setExpensesList(data.reports);
      setExpenseData(formattedData);
    } catch (error) {
      console.error("Error loading expense data:", error);
      Alert.alert("Error", "Failed to load expense data.");
    } finally {
      setLoading(false);
    }
  };

  // Handle Edit Expense
  const handleEditExpense = async (expense) => {
    try {
      await editExpense(expense.id, editedValues);
      Alert.alert("Success", "Expense updated successfully!");
      setEditMode(null);
      loadExpenseData();
    } catch (error) {
      console.error("Error editing expense:", error);
      Alert.alert("Error", "Failed to edit expense.");
    }
  };

  // Handle Delete Expense
  const handleDeleteExpense = async (expenseId) => {
    Alert.alert("Confirm Delete", "Are you sure you want to delete this expense?", [
      { text: "Cancel", style: "cancel" },
      {
        text: "Delete",
        onPress: async () => {
          try {
            await deleteExpense(expenseId);
            Alert.alert("Success", "Expense deleted successfully!");
            loadExpenseData();
          } catch (error) {
            console.error("Error deleting expense:", error);
            Alert.alert("Error", "Failed to delete expense.");
          }
        },
        style: "destructive",
      },
    ]);
  };

  // Render Expense Item
  const renderExpenseItem = ({ item }) => (
    <View style={styles.expenseItem}>
      {editMode === item.id ? (
        <>
          <TextInput
            style={styles.input}
            placeholder="Description"
            defaultValue={item.description}
            onChangeText={(value) => setEditedValues({ ...editedValues, description: value })}
          />
          <TextInput
            style={styles.input}
            placeholder="Amount"
            defaultValue={item.amount.toString()}
            keyboardType="numeric"
            onChangeText={(value) => setEditedValues({ ...editedValues, amount: parseFloat(value) })}
          />
          <Button title="Save" onPress={() => handleEditExpense(item)} color="#28a745" />
          <Button title="Cancel" onPress={() => setEditMode(null)} color="#dc3545" />
        </>
      ) : (
        <>
          <Text style={styles.expenseText}>
            {item.category}: ${item.amount} ({item.description})
          </Text>
          <View style={styles.buttonRow}>
            <Button title="Edit" onPress={() => setEditMode(item.id)} color="#007BFF" />
            <Button title="Delete" onPress={() => handleDeleteExpense(item.id)} color="#FF5733" />
          </View>
        </>
      )}
    </View>
  );

  return (
    <View style={styles.container}>
      {/* Logout Button */}
      <View style={styles.logoutContainer}>
        <Button title="Logout" onPress={onLogout} color="#FF5733" />
      </View>

      <Text style={styles.title}>Expense Summary</Text>
      {loading ? (
        <ActivityIndicator size="large" color="#007BFF" />
      ) : (
        <VictoryChart theme={VictoryTheme.material} domainPadding={20}>
          <VictoryBar data={expenseData} style={{ data: { fill: "#007BFF" } }} />
        </VictoryChart>
      )}

      <Text style={styles.title}>Expense Breakdown</Text>
      {loading ? (
        <ActivityIndicator size="large" color="#007BFF" />
      ) : (
        <VictoryPie
          data={expenseData}
          colorScale={["tomato", "orange", "gold", "cyan", "navy"]}
          labels={({ datum }) => `${datum.x}: ${datum.y}`}
          style={{ labels: { fontSize: 14, fontWeight: "bold" } }}
        />
      )}

      {/* Expense List */}
      <Text style={styles.title}>Expenses List</Text>
      <FlatList
        data={expensesList}
        keyExtractor={(item) => item.id.toString()}
        renderItem={renderExpenseItem}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, backgroundColor: "#f9f9f9" },
  title: { fontSize: 22, fontWeight: "bold", textAlign: "center", marginVertical: 10 },
  logoutContainer: { alignItems: "flex-end", marginBottom: 10 },
  expenseItem: {
    padding: 10,
    marginVertical: 5,
    backgroundColor: "#e7f3ff",
    borderRadius: 5,
  },
  expenseText: { fontSize: 16, color: "#333" },
  buttonRow: { flexDirection: "row", justifyContent: "space-between", marginTop: 5 },
  input: {
    borderWidth: 1,
    borderColor: "#ccc",
    padding: 5,
    marginVertical: 5,
    borderRadius: 5,
  },
});

export default DashboardScreen;
