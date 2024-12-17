import React, { useEffect, useState } from "react";
import { View, Text, StyleSheet, FlatList, ActivityIndicator, Alert } from "react-native";
import { fetchIRSReports, fetchExpenseReports } from "../services/reportsService";

const ReportsScreen = () => {
  const [irsReports, setIRSReports] = useState([]);
  const [expenseReports, setExpenseReports] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadReports = async () => {
      try {
        const irsData = await fetchIRSReports();
        const expenseData = await fetchExpenseReports();
        setIRSReports(irsData.reports || []);
        setExpenseReports(expenseData.reports || []);
      } catch (error) {
        Alert.alert("Error", "Failed to load reports.");
      } finally {
        setLoading(false);
      }
    };

    loadReports();
  }, []);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>IRS-Ready Reports</Text>
      {loading ? (
        <ActivityIndicator size="large" color="#007BFF" />
      ) : (
        <FlatList
          data={irsReports}
          keyExtractor={(item, index) => index.toString()}
          renderItem={({ item }) => <Text style={styles.item}>{item}</Text>}
        />
      )}
      <Text style={styles.title}>Expense Breakdown</Text>
      <FlatList
        data={expenseReports}
        keyExtractor={(item, index) => index.toString()}
        renderItem={({ item }) => <Text style={styles.item}>{item}</Text>}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, backgroundColor: "#f9f9f9" },
  title: { fontSize: 22, fontWeight: "bold", marginVertical: 10 },
  item: { padding: 10, borderBottomWidth: 1, borderBottomColor: "#ccc" },
});

export default ReportsScreen;
