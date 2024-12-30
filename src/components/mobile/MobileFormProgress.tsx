import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Text } from 'react-native-paper';
import { COLORS } from '../../../assets/config/colors';
import { SPACING } from '../../../assets/config/spacing';
import { TYPOGRAPHY } from '../../../assets/config/typography';

interface MobileFormProgressProps {
  steps: string[];
  currentStep: number;
}

export const MobileFormProgress: React.FC<MobileFormProgressProps> = ({
  steps,
  currentStep
}) => {
  return (
    <View style={styles.container}>
      <View style={styles.progressBar}>
        {steps.map((step, index) => (
          <React.Fragment key={index}>
            <View
              style={[
                styles.step,
                index <= currentStep && styles.activeStep
              ]}
            >
              <Text style={[
                styles.stepNumber,
                index <= currentStep && styles.activeStepNumber
              ]}>
                {index + 1}
              </Text>
            </View>
            {index < steps.length - 1 && (
              <View
                style={[
                  styles.connector,
                  index < currentStep && styles.activeConnector
                ]}
              />
            )}
          </React.Fragment>
        ))}
      </View>
      <View style={styles.labels}>
        {steps.map((step, index) => (
          <Text
            key={index}
            style={[
              styles.stepLabel,
              index === currentStep && styles.activeStepLabel
            ]}
          >
            {step}
          </Text>
        ))}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: SPACING.md
  },
  progressBar: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between'
  },
  step: {
    width: 30,
    height: 30,
    borderRadius: 15,
    backgroundColor: COLORS.surface,
    justifyContent: 'center',
    alignItems: 'center'
  },
  activeStep: {
    backgroundColor: COLORS.primary
  },
  stepNumber: {
    color: COLORS.text.secondary,
    fontSize: TYPOGRAPHY.fontSize.sm,
    fontFamily: TYPOGRAPHY.fontFamily.medium
  },
  activeStepNumber: {
    color: '#fff'
  },
  connector: {
    flex: 1,
    height: 2,
    backgroundColor: COLORS.surface,
    marginHorizontal: SPACING.sm
  },
  activeConnector: {
    backgroundColor: COLORS.primary
  },
  labels: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 8
  },
  stepLabel: {
    fontSize: TYPOGRAPHY.fontSize.xs,
    color: COLORS.text.secondary,
    textAlign: 'center'
  },
  activeStepLabel: {
    color: COLORS.primary,
    fontWeight: '600'
  }
});
