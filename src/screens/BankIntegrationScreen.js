import React, { useState } from "react";
import {
  View,
  Text,
  TextInput,
  Button,
  FlatList,
  StyleSheet,
  Alert,
  ActivityIndicator,
} from "react-native";
import {
  connectBankAccount,
  getBankTransactions,
} from "../services/bankService";

const BankIntegrationScreen = ({ userId }) => {
  const [bankName, setBankName] = useState("");
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(false);

  // Connect Bank Account
  const handleConnectBank = async () => {
    if (!bankName) {
      Alert.alert("Error", "Please enter a bank name.");
      return;
    }

    try {
      setLoading(true);
      const response = await connectBankAccount(userId, bankName);
      Alert.alert("Success", response.message || "Bank account connected successfully!");
    } catch (error) {
      console.error("Error connecting bank account:", error.message);
      Alert.alert("Error", "Failed to connect bank account.");
    } finally {
      setLoading(false);
    }
  };

  // Fetch Bank Transactions
  const handleFetchTransactions = async () => {
    try {
      setLoading(true);
      const data = await getBankTransactions(userId);
      setTransactions(data.transactions || []);
    } catch (error) {
      console.error("Error fetching transactions:", error.message);
      Alert.alert("Error", "Failed to fetch transactions.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Bank Integration</Text>

      {/* Bank Name Input */}
      <TextInput
        style={styles.input}
        placeholder="Enter Bank Name"
        value={bankName}
        onChangeText={setBankName}
      />

      {/* Connect Bank Account Button */}
      <Button title="Connect Bank Account" onPress={handleConnectBank} color="#007BFF" />

      {/* Fetch Transactions Button */}
      <View style={styles.fetchButton}>
        <Button title="Fetch Transactions" onPress={handleFetchTransactions} color="#28A745" />
      </View>

      {/* Loading State */}
      {loading && <ActivityIndicator size="large" color="#007BFF" />}

      {/* Transactions List */}
      {transactions.length > 0 && (
        <View style={styles.transactionsContainer}>
          <Text style={styles.subtitle}>Transactions</Text>
          <FlatList
            data={transactions}
            keyExtractor={(item, index) => index.toString()}
            renderItem={({ item }) => (
              <View style={styles.transactionItem}>
                <Text>{item.date} - {item.description}</Text>
                <Text style={styles.amount}>${item.amount}</Text>
              </View>
            )}
          />
        </View>
      )}

      {transactions.length === 0 && !loading && (
        <Text style={styles.noDataText}>No transactions found.</Text>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, backgroundColor: "#f9f9f9" },
  title: { fontSize: 22, fontWeight: "bold", textAlign: "center", marginBottom: 20 },
  input: {
    borderWidth: 1,
    borderColor: "#ccc",
    padding: 10,
    marginBottom: 10,
    borderRadius: 5,
    backgroundColor: "#fff",
  },
  fetchButton: { marginTop: 10 },
  transactionsContainer: { marginTop: 20 },
  subtitle: { fontSize: 18, fontWeight: "bold", marginBottom: 10 },
  transactionItem: {
    padding: 10,
    backgroundColor: "#e7f3ff",
    borderRadius: 5,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: "#007BFF",
  },
  amount: { fontWeight: "bold", color: "#28A745", textAlign: "right" },
  noDataText: { textAlign: "center", color: "#777", marginTop: 20 },
});

export default BankIntegrationScreen;
