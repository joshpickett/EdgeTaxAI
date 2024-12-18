import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  ActivityIndicator,
  Alert,
  Button,
  TextInput,
} from "react-native";
import { fetchIRSReports, fetchCustomReports } from "../services/reportsService";
import * as FileSystem from "expo-file-system";
import * as Sharing from "expo-sharing";

const ReportsScreen = ({ userId }) => {
  const [irsReports, setIRSReports] = useState(null);
  const [customReports, setCustomReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    startDate: "",
    endDate: "",
    category: "",
  });

  // Fetch IRS-Ready Reports on Component Mount
  useEffect(() => {
    const loadIRSReports = async () => {
      try {
        const data = await fetchIRSReports(userId);
        setIRSReports(data);
      } catch (error) {
        Alert.alert("Error", "Failed to load IRS-ready reports.");
      } finally {
        setLoading(false);
      }
    };

    loadIRSReports();
  }, [userId]);

  // Function to Download Reports
  const handleDownload = async (url, fileName) => {
    try {
      const fileUri = `${FileSystem.documentDirectory}${fileName}`;
      const result = await FileSystem.downloadAsync(url, fileUri);

      if (await Sharing.isAvailableAsync()) {
        await Sharing.shareAsync(result.uri);
      } else {
        Alert.alert("Error", "Sharing is not supported on this device.");
      }
    } catch (error) {
      console.error("Error downloading file:", error);
      Alert.alert("Error", "Failed to download the report.");
    }
  };

  // Fetch Custom Reports
  const handleFetchCustomReports = async () => {
    try {
      setLoading(true);
      const data = await fetchCustomReports(userId, filters);
      setCustomReports(data);
    } catch (error) {
      Alert.alert("Error", "Failed to fetch custom reports.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>IRS-Ready Reports</Text>

      {loading ? (
        <ActivityIndicator size="large" color="#007BFF" />
      ) : (
        <>
          {/* Download Buttons */}
          <Button
            title="Download PDF Report"
            onPress={() => handleDownload(irsReports.pdf, "irs_report.pdf")}
          />
          <Button
            title="Download CSV Report"
            onPress={() => handleDownload(irsReports.csv, "irs_report.csv")}
          />

          <Text style={styles.subtitle}>Generate Custom Reports</Text>

          {/* Filters */}
          <TextInput
            placeholder="Start Date (YYYY-MM-DD)"
            style={styles.input}
            value={filters.startDate}
            onChangeText={(value) => setFilters({ ...filters, startDate: value })}
          />
          <TextInput
            placeholder="End Date (YYYY-MM-DD)"
            style={styles.input}
            value={filters.endDate}
            onChangeText={(value) => setFilters({ ...filters, endDate: value })}
          />
          <TextInput
            placeholder="Category"
            style={styles.input}
            value={filters.category}
            onChangeText={(value) => setFilters({ ...filters, category: value })}
          />

          <Button title="Fetch Custom Reports" onPress={handleFetchCustomReports} />

          {/* Custom Reports Display */}
          {customReports.length > 0 && (
            <FlatList
              data={customReports}
              keyExtractor={(item, index) => index.toString()}
              renderItem={({ item }) => (
                <Text style={styles.item}>
                  {item.description}: ${item.amount} ({item.category})
                </Text>
              )}
            />
          )}
        </>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, backgroundColor: "#f9f9f9" },
  title: { fontSize: 22, fontWeight: "bold", marginBottom: 20, textAlign: "center" },
  subtitle: { fontSize: 18, marginTop: 20, marginBottom: 10, fontWeight: "bold" },
  input: { borderWidth: 1, borderColor: "#ccc", padding: 10, marginBottom: 10, borderRadius: 5 },
  item: { padding: 10, borderBottomWidth: 1, borderColor: "#ddd" },
});

export default ReportsScreen;
