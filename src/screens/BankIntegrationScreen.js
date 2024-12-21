import React, { useState } from "react";
import {
  View,
  Text,
  Button,
  FlatList,
  StyleSheet,
  Alert,
  ActivityIndicator,
} from "react-native";
import { bankService } from "../services/bankService";
import { useSelector } from 'react-redux';
import DateTimePicker from '@react-native-community/datetimepicker';

const BankIntegrationScreen = ({ userId }) => {
  const [bankName, setBankName] = useState("");
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [startDate, setStartDate] = useState(new Date());
  const [endDate, setEndDate] = useState(new Date());

  // Connect Bank Account
  const handleConnectBank = async () => {
    if (!bankName) {
      Alert.alert("Error", "Please enter a bank name.");
      return;
    }

    try {
      setLoading(true);
      const response = await bankService.getLinkToken(userId);
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
      const data = await bankService.getTransactions({
        start_date: startDate.toISOString().split('T')[0],
        end_date: endDate.toISOString().split('T')[0],
        user_id: userId
      });
      setTransactions(data.transactions || []);
    } catch (error) {
      console.error("Error fetching transactions:", error.message);
      Alert.alert("Error", "Failed to fetch transactions.");
    } finally {
      setLoading(false);
    }
  };

  const handleCheckBalance = async () => {
    try {
      setLoading(true);
      const data = await bankService.getBalance(userId);
      Alert.alert("Account Balance", `Current Balance: $${data.balance}`);
    } catch (error) {
      console.error("Error checking balance:", error.message);
      Alert.alert("Error", "Failed to fetch balance.");
    } finally {
      setLoading(false);
    }
  };

  const handleDateRangeSelect = (start, end) => {
    setStartDate(start);
    setEndDate(end);
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

      {/* Check Balance Button */}
      <View style={styles.balanceButton}>
        <Button title="Check Balance" onPress={handleCheckBalance} color="#28A745" />
      </View>

      {/* Date Range Picker */}
      <DateRangePicker onSelect={handleDateRangeSelect} />

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
  balanceButton: { marginTop: 10 },
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
