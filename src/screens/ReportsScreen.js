import React, { useState } from "react";
import {
  View,
  Text,
  TextInput,
  Button,
  FlatList,
  StyleSheet,
  ActivityIndicator,
  Alert,
  Linking,
} from "react-native";
import { fetchIRSReports, fetchCustomReports } from "../services/reportsService";

const BASE_URL = "https://your-backend-api.com/api/reports";

const ReportsScreen = ({ navigation }) => {
  const [filters, setFilters] = useState({
    startDate: "",
    endDate: "",
    category: "",
  });
  const [loading, setLoading] = useState(false);
  const [customReports, setCustomReports] = useState([]);
  const [irsReports, setIRSReports] = useState(null);

  // Fetch IRS Reports
  const handleFetchIRSReports = async () => {
    setLoading(true);
    try {
      const data = await fetchIRSReports();
      setIRSReports(data);
      Alert.alert("Success", "IRS Reports loaded successfully.");
    } catch (error) {
      console.error("Error fetching IRS Reports:", error.message);
      Alert.alert("Error", error.message || "Failed to fetch IRS Reports.");
    } finally {
      setLoading(false);
    }
  };

  // Fetch Custom Reports
  const handleFetchCustomReports = async () => {
    if (!filters.startDate || !filters.endDate) {
      Alert.alert("Error", "Start Date and End Date are required.");
      return;
    }

    setLoading(true);
    try {
      const data = await fetchCustomReports(filters);
      if (data.length === 0) {
        Alert.alert("No Data", "No reports found for the selected filters.");
      }
      setCustomReports(data);
    } catch (error) {
      console.error("Error fetching Custom Reports:", error.message);
      Alert.alert("Error", error.message || "Failed to fetch custom reports.");
    } finally {
      setLoading(false);
    }
  };

  // Navigate to Gig Platform Screen
  const handleNavigateToGigPlatforms = () => {
    navigation.navigate("GigPlatforms");
  };

  // Render Custom Reports Item
  const renderReportItem = ({ item }) => (
    <View style={styles.reportItem}>
      <Text style={styles.reportText}>
        {item.date} - {item.description}: ${item.amount}
      </Text>
    </View>
  );

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Reports Dashboard</Text>

      {/* IRS Reports Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>IRS-Ready Reports</Text>
        <Button title="Fetch IRS Reports" onPress={handleFetchIRSReports} color="#007BFF" />
        {loading && <ActivityIndicator size="small" color="#007BFF" />}
        {irsReports && (
          <Text style={styles.reportText}>
            IRS Report: {JSON.stringify(irsReports, null, 2)}
          </Text>
        )}
      </View>

      {/* Gig Platform Integration Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Connect Gig Platforms</Text>
        <Text style={styles.description}>
          Manage your gig platform accounts to import trip and expense data (e.g., Uber, Lyft,
          DoorDash, Instacart, Upwork, Fiverr).
        </Text>
        <Button
          title="Manage Gig Platforms"
          onPress={handleNavigateToGigPlatforms}
          color="#28A745"
        />
      </View>

      {/* Custom Reports Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Custom Reports</Text>

        {/* Input Filters */}
        <TextInput
          style={styles.input}
          placeholder="Start Date (YYYY-MM-DD)"
          value={filters.startDate}
          onChangeText={(value) => setFilters({ ...filters, startDate: value })}
        />
        <TextInput
          style={styles.input}
          placeholder="End Date (YYYY-MM-DD)"
          value={filters.endDate}
          onChangeText={(value) => setFilters({ ...filters, endDate: value })}
        />
        <TextInput
          style={styles.input}
          placeholder="Category (Optional)"
          value={filters.category}
          onChangeText={(value) => setFilters({ ...filters, category: value })}
        />

        <Button title="Fetch Custom Reports" onPress={handleFetchCustomReports} color="#17A2B8" />

        {/* Loading State */}
        {loading && <ActivityIndicator size="small" color="#17A2B8" />}

        {/* Custom Reports List */}
        {customReports.length > 0 ? (
          <FlatList
            data={customReports}
            keyExtractor={(item, index) => index.toString()}
            renderItem={renderReportItem}
          />
        ) : (
          !loading && <Text style={styles.noDataText}>No custom reports found.</Text>
        )}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, backgroundColor: "#f9f9f9" },
  title: { fontSize: 22, fontWeight: "bold", textAlign: "center", marginBottom: 20 },
  section: { marginBottom: 30 },
  sectionTitle: { fontSize: 18, fontWeight: "bold", marginBottom: 10 },
  description: { fontSize: 14, color: "#555", marginBottom: 10 },
  input: {
    borderWidth: 1,
    borderColor: "#ccc",
    padding: 10,
    marginBottom: 10,
    borderRadius: 5,
    backgroundColor: "#fff",
  },
  reportItem: {
    padding: 10,
    marginBottom: 10,
    backgroundColor: "#e7f3ff",
    borderRadius: 5,
    borderWidth: 1,
    borderColor: "#007BFF",
  },
  reportText: { fontSize: 16, color: "#333" },
  noDataText: { textAlign: "center", color: "#777" },
});

export default ReportsScreen;