import React, { useEffect, useState } from "react";
import { View, Text, StyleSheet, ActivityIndicator } from "react-native";
import { VictoryPie, VictoryBar, VictoryChart, VictoryTheme } from "victory-native";
import { fetchExpenseReports } from "../services/reportsService";

const DashboardScreen = () => {
  const [expenseData, setExpenseData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load expense data on component mount
    const loadExpenseData = async () => {
      try {
        const data = await fetchExpenseReports();

        // Format data for Victory Charts
        const formattedData = data.reports.map((item) => ({
          x: item.category, // X-axis: Category name
          y: item.amount,   // Y-axis: Expense amount
        }));
        setExpenseData(formattedData);
      } catch (error) {
        console.error("Error loading expense data:", error);
      } finally {
        setLoading(false);
      }
    };

    loadExpenseData();
  }, []);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Expense Summary</Text>

      {loading ? (
        <ActivityIndicator size="large" color="#007BFF" />
      ) : (
        <VictoryChart theme={VictoryTheme.material} domainPadding={20}>
          <VictoryBar
            data={expenseData}
            style={{ data: { fill: "#007BFF" } }} // Bar color
          />
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
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, backgroundColor: "#f9f9f9" },
  title: { fontSize: 22, fontWeight: "bold", textAlign: "center", marginVertical: 10 },
});

export default DashboardScreen;
