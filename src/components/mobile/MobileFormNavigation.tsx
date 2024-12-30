import React from 'react';
import { View, StyleSheet, TouchableOpacity } from 'react-native';
import { Text } from 'react-native-paper';
import { COLORS } from '../../../assets/config/colors';
import { SPACING } from '../../../assets/config/spacing';
import { TYPOGRAPHY } from '../../../assets/config/typography';
import Icon from 'react-native-vector-icons/MaterialIcons';

interface MobileFormNavigationProps {
  onNext?: () => void;
  onBack?: () => void;
  canGoNext?: boolean;
  canGoBack?: boolean;
  nextLabel?: string;
  backLabel?: string;
}

export const MobileFormNavigation: React.FC<MobileFormNavigationProps> = ({
  onNext,
  onBack,
  canGoNext = true,
  canGoBack = true,
  nextLabel = 'Next',
  backLabel = 'Back'
}) => {
  return (
    <View style={styles.container}>
      {canGoBack && (
        <TouchableOpacity 
          style={styles.button} 
          onPress={onBack}
          disabled={!canGoBack}
        >
          <Icon name="arrow-back" size={20} color="#666" />
          <Text style={styles.buttonText}>{backLabel}</Text>
        </TouchableOpacity>
      )}
      
      {canGoNext && (
        <TouchableOpacity 
          style={[styles.button, styles.nextButton]} 
          onPress={onNext}
          disabled={!canGoNext}
        >
          <Text style={[styles.buttonText, styles.nextButtonText]}>
            {nextLabel}
          </Text>
          <Icon name="arrow-forward" size={20} color="#fff" />
        </TouchableOpacity>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    padding: SPACING.md,
    borderTopWidth: 1,
    borderTopColor: COLORS.divider,
    backgroundColor: COLORS.background
  },
  button: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: SPACING.sm,
    borderRadius: 8
  },
  buttonText: {
    marginHorizontal: SPACING.sm,
    fontSize: TYPOGRAPHY.fontSize.md
  },
  nextButton: {
    backgroundColor: COLORS.primary,
    paddingHorizontal: SPACING.md
  },
  nextButtonText: {
    color: '#fff'
  }
});
