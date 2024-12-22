import React, { useEffect, useState, useCallback } from "react";
import { ScrollView, RefreshControl, StyleSheet } from "react-native";
import DashboardOverview from "../components/DashboardOverview";
import { sharedReportingService } from "../services/sharedReportingService";

const DashboardScreen = ({ onLogout }) => {
  const [dashboardData, setDashboardData] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = useCallback(async () => {
    setRefreshing(true);
    try {
      const data = await sharedReportingService.fetchDashboardData();
      setDashboardData(data);
    } catch (error) {
      console.error("Error loading dashboard:", error);
    } finally {
      setRefreshing(false);
    }
  }, []);

  return (
    <ScrollView 
      style={styles.container}
      refreshControl={
        <RefreshControl
          refreshing={refreshing}
          onRefresh={loadDashboardData}
        />
      }
    >
      {dashboardData && <DashboardOverview data={dashboardData} />}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, backgroundColor: '#f5f5f5' },
});

export default DashboardScreen;
