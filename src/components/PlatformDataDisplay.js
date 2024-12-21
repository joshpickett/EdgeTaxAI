import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Card } from 'react-native-elements';

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount);
};

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString();
};

const PlatformDataDisplay = ({ platform, data }) => {
  const renderUberData = () => (
    <Card>
      <Card.Title>Uber Earnings Summary</Card.Title>
      <View style={styles.dataRow}>
        <Text>Total Trips: {data.trips_count}</Text>
        <Text>Gross Earnings: {formatCurrency(data.gross_earnings)}</Text>
      </View>
      <View style={styles.dataRow}>
        <Text>Net Earnings: {formatCurrency(data.net_earnings)}</Text>
        <Text>Time Period: {formatDate(data.period_start)} - {formatDate(data.period_end)}</Text>
      </View>
    </Card>
  );

  const renderLyftData = () => (
    <Card>
      <Card.Title>Lyft Earnings Summary</Card.Title>
      <View style={styles.dataRow}>
        <Text>Total Rides: {data.rides_count}</Text>
        <Text>Gross Earnings: {formatCurrency(data.gross_earnings)}</Text>
      </View>
      <View style={styles.dataRow}>
        <Text>Net Earnings: {formatCurrency(data.net_earnings)}</Text>
        <Text>Time Period: {formatDate(data.period_start)} - {formatDate(data.period_end)}</Text>
      </View>
    </Card>
  );

  const renderDoorDashData = () => (
    <Card>
      <Card.Title>DoorDash Earnings Summary</Card.Title>
      <View style={styles.dataRow}>
        <Text>Total Deliveries: {data.deliveries_count}</Text>
        <Text>Gross Earnings: {formatCurrency(data.gross_earnings)}</Text>
      </View>
      <View style={styles.dataRow}>
        <Text>Net Earnings: {formatCurrency(data.net_earnings)}</Text>
        <Text>Time Period: {formatDate(data.period_start)} - {formatDate(data.period_end)}</Text>
      </View>
    </Card>
  );

  const getPlatformDisplay = () => {
    switch (platform) {
      case 'uber':
        return renderUberData();
      case 'lyft':
        return renderLyftData();
      case 'doordash':
        return renderDoorDashData();
      default:
        return (
          <Card>
            <Card.Title>{platform.toUpperCase()} Data</Card.Title>
            <Text>No specific display format available</Text>
          </Card>
        );
    }
  };

  return (
    <View style={styles.container}>
      {getPlatformDisplay()}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    margin: 10,
  },
  dataRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginVertical: 5,
  },
});

export default PlatformDataDisplay;
