import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Card } from 'react-native-elements';
import { VictoryPie } from 'victory-native';

const TaxSummaryCard = ({ taxData }) => {
  return (
    <Card containerStyle={styles.container}>
      <Card.Title>Quarterly Tax Summary</Card.Title>
      <View style={styles.content}>
        <View style={styles.infoContainer}>
          <Text style={styles.label}>Current Quarter:</Text>
          <Text style={styles.quarterText}>Q{taxData.currentQuarter}</Text>

          <Text style={styles.label}>Estimated Tax Due:</Text>
          <Text style={styles.amount}>${taxData.estimatedTax}</Text>
          
          <Text style={styles.label}>YTD Tax Paid:</Text>
          <Text style={styles.amount}>${taxData.ytdTaxPaid}</Text>

          <Text style={styles.label}>Next Payment Due:</Text>
          <Text style={styles.date}>{taxData.nextPaymentDate}</Text>
          
          <Text style={styles.label}>Current Tax Rate:</Text>
          <Text style={styles.rate}>{taxData.effectiveRate}%</Text>
        </View>
        
        <View style={styles.chartContainer}>
          <VictoryPie
            data={[
              { x: "Tax", y: taxData.estimatedTax },
              { x: "Net", y: taxData.netIncome }
            ]}
            colorScale={["#FF6B6B", "#4ECDC4"]}
            labels={({ datum }) => `${datum.x}: $${datum.y}`}
          />
        </View>
      </View>
    </Card>
  );
};

const styles = StyleSheet.create({
  container: {
    borderRadius: 10,
    marginBottom: 15,
    elevation: 3
  },
  content: {
    flexDirection: 'row',
    justifyContent: 'space-between'
  },
  infoContainer: {
    flex: 1,
    padding: 10
  },
  chartContainer: {
    flex: 1,
    alignItems: 'center'
  },
  label: {
    fontSize: 14,
    color: '#666',
    marginBottom: 5
  },
  amount: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#FF6B6B',
    marginBottom: 10
  },
  date: {
    fontSize: 16,
    color: '#333',
    marginBottom: 10
  },
  rate: {
    fontSize: 16,
    color: '#4ECDC4'
  },
  quarterText: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#007AFF',
    marginBottom: 15
  },
  progressBar: {
    height: 10,
    backgroundColor: '#E0E0E0',
    borderRadius: 5,
    marginTop: 10
  },
  progress: {
    height: '100%',
    backgroundColor: '#4ECDC4',
    borderRadius: 5
  }
});

export default TaxSummaryCard;
