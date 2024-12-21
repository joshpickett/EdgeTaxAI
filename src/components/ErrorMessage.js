import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { colors, typography, spacing } from '../styles/tokens';

const ErrorMessage = ({ message, type = 'error' }) => {
  const getStyle = () => {
    switch (type) {
      case 'success':
        return styles.success;
      case 'warning':
        return styles.warning;
      default:
        return styles.error;
    }
  };

  return (
    <View style={[styles.container, getStyle()]}>
      <Text style={styles.text}>{message}</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: spacing.md,
    borderRadius: 4,
    borderWidth: 1,
    marginVertical: spacing.sm
  },
  text: {
    fontFamily: typography.fontFamily.primary,
    fontSize: typography.fontSize.sm,
    fontWeight: typography.fontWeight.medium
  }
});

export default ErrorMessage;
