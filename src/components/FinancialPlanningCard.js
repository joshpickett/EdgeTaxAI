import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Card, Button } from 'react-native-elements';
import { VictoryPie, VictoryBar } from 'victory-native';

const FinancialPlanningCard = ({ planningData }) => {
  return (
    <Card containerStyle={styles.container}>
      <Card.Title>Financial Planning</Card.Title>
      
      <View style={styles.goalsSection}>
        <Text style={styles.sectionTitle}>Income Goals</Text>
        <View style={styles.goalProgress}>
          <Text>Monthly Goal: ${planningData.monthlyGoal}</Text>
          <Text>Progress: ${planningData.currentMonthly} ({planningData.monthlyProgress}%)</Text>
          <View style={styles.progressBar}>
            <View 
              style={[
                styles.progress, 
                { width: `${planningData.monthlyProgress}%` }
              ]} 
            />
          </View>
        </View>
      </View>

      <View style={styles.savingsSection}>
        <Text style={styles.sectionTitle}>Tax Savings</Text>
        <Text style={styles.recommendedSavings}>
          Recommended Monthly Savings: ${planningData.recommendedSavings}
        </Text>
        <VictoryPie
          data={planningData.savingsBreakdown}
          colorScale={["#FF6B6B", "#4ECDC4", "#45B7D1"]}
          labels={({ datum }) => `${datum.x}: $${datum.y}`}
          height={200}
        />
      </View>

      <View style={styles.projectionsSection}>
        <Text style={styles.sectionTitle}>Quarterly Projections</Text>
        <VictoryBar
          data={planningData.quarterlyProjections}
          x="quarter"
          y="amount"
          style={{
            data: { fill: "#007AFF" }
          }}
        />
      </View>

      <Button
        title="Update Financial Goals"
        onPress={planningData.onUpdateGoals}
        type="outline"
        containerStyle={styles.buttonContainer}
      />
    </Card>
  );
};

const styles = StyleSheet.create({
  container: {
    borderRadius: 10,
    marginBottom: 15,
    elevation: 3,
    padding: 15
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10
  },
  goalsSection: {
    marginBottom: 20
  },
  goalProgress: {
    marginTop: 10
  },
  progressBar: {
    height: 10,
    backgroundColor: '#E0E0E0',
    borderRadius: 5,
    marginTop: 5
  },
  progress: {
    height: '100%',
    backgroundColor: '#4ECDC4',
    borderRadius: 5
  },
  savingsSection: {
    marginBottom: 20
  },
  recommendedSavings: {
    fontSize: 16,
    color: '#007AFF',
    marginBottom: 10
  },
  projectionsSection: {
    marginBottom: 20
  },
  buttonContainer: {
    marginTop: 10
  }
});

export default FinancialPlanningCard;