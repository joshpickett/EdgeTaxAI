import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Card, Text, Chip, List, ActivityIndicator } from 'react-native-paper';
import { COLORS } from '../../assets/config/colors';
import { SPACING } from '../../assets/config/spacing';

export const PlatformDataDisplay = ({ platformData, isLoading, error }) => {
  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" />
        <Text style={styles.loadingText}>Loading platform data...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorText}>Error loading platform data: {error}</Text>
      </View>
    );
  }

  return (
    <Card style={styles.container}>
      <Card.Content>
        <View style={styles.header}>
          <Text style={styles.title}>Platform Summary</Text>
          <Chip icon="sync" mode="outlined">
            Last synced: {platformData?.lastSync || 'Never'}
          </Chip>
        </View>

        <List.Section>
          <List.Subheader>Income Summary</List.Subheader>
          <List.Item
            title="Total Earnings"
            description={`$${platformData?.totalEarnings || '0.00'}`}
            left={props => <List.Icon {...props} icon="cash" />}
          />
          <List.Item
            title="Number of Transactions"
            description={platformData?.transactionCount || '0'}
            left={props => <List.Icon {...props} icon="receipt" />}
          />
        </List.Section>

        <List.Section>
          <List.Subheader>Tax Documents</List.Subheader>
          {platformData?.taxDocuments?.map((doc, index) => (
            <List.Item
              key={index}
              title={doc.type}
              description={doc.status}
              left={props => <List.Icon {...props} icon="file-document" />}
            />
          ))}
        </List.Section>
      </Card.Content>
    </Card>
  );
};

const styles = StyleSheet.create({
  container: {
    margin: SPACING.md,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: SPACING.md,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: SPACING.xl,
  },
  loadingText: {
    marginTop: SPACING.md,
    color: COLORS.text.secondary,
  },
  errorContainer: {
    padding: SPACING.md,
    backgroundColor: COLORS.error,
    margin: SPACING.md,
    borderRadius: 8,
  },
  errorText: {
    color: '#fff',
  },
});
