import React from 'react';
import { View, StyleSheet } from 'react-native';
import TaxSummaryCard from './TaxSummaryCard';
import IncomeTrendChart from './IncomeTrendChart';
import FinancialPlanningCard from './FinancialPlanningCard';
import ExpenseSummaryCard from './ExpenseSummaryCard';

const DashboardOverview = ({ data }) => {
  const {
    taxData,
    incomeData,
    expenseData,
    planningData
  } = data;

  return (
    <View style={styles.container}>
      <TaxSummaryCard taxData={taxData} />
      <IncomeTrendChart data={incomeData} />
      <ExpenseSummaryCard data={expenseData} />
      <FinancialPlanningCard planningData={planningData} />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 15
  }
});

export default DashboardOverview;
