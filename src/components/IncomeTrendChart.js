import React, { useState } from 'react';
import { View, StyleSheet, Dimensions } from 'react-native';
import { setupSrcPath } from '../setup_path';
import { VictoryLine, VictoryChart, VictoryAxis, VictoryTheme } from 'victory-native';
import { colors, typography, spacing } from '../styles/tokens';
import { Card } from 'react-native-elements';

const IncomeTrendChart = ({ data }) => {
  const [selectedPeriod, setSelectedPeriod] = useState('monthly');

  return (
    <Card containerStyle={styles.container}>
      <Card.Title>Income Trends</Card.Title>
      
      <View style={styles.periodSelector}>
        <Button 
          title="Monthly"
          onPress={() => setSelectedPeriod('monthly')}
          type={selectedPeriod === 'monthly' ? 'solid' : 'outline'}
        />
        <Button
          title="Quarterly"
          onPress={() => setSelectedPeriod('quarterly')}
          type={selectedPeriod === 'quarterly' ? 'solid' : 'outline'}
        />
        <Button
          title="Yearly"
          onPress={() => setSelectedPeriod('yearly')}
          type={selectedPeriod === 'yearly' ? 'solid' : 'outline'}
        />
      </View>

      <View style={styles.chartContainer}>
        <VictoryChart
          theme={VictoryTheme.material}
          width={Dimensions.get('window').width - 60}
          height={250}
        >
          <VictoryAxis
            tickFormat={(x) => `${x.getMonth() + 1}/${x.getFullYear()}`}
            style={{
              tickLabels: { angle: -45, fontSize: 8 }
            }}
          />
          <VictoryAxis
            dependentAxis
            tickFormat={(y) => `$${y}`}
          />
          <VictoryLine
            data={data}
            x="date"
            y="amount"
            style={{
              data: { stroke: colors.primary.main }
            }}
          />
        </VictoryChart>
      </View>
    </Card>
  );
};

const styles = StyleSheet.create({
  container: {
    borderRadius: spacing.md,
    marginBottom: spacing.md,
    elevation: spacing.xs,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25
  },
  chartContainer: {
    alignItems: 'center',
    marginTop: spacing.sm
  },
  periodSelector: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: spacing.md
  },
  legend: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginTop: spacing.sm
  },
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginHorizontal: spacing.md
  },
});

export default IncomeTrendChart;
