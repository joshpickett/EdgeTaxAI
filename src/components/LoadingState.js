import React from 'react';
import { View, ActivityIndicator, Text, StyleSheet } from 'react-native';
import { setupSrcPath } from '../setup_path';
setupSrcPath();
import { colors, typography, spacing } from '../styles/tokens';

const LoadingState = ({ message = 'Loading...' }) => {
  return (
    <View style={styles.container}>
      <ActivityIndicator size="large" color={colors.primary.main} />
      <Text style={styles.message}>{message}</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background.default,
    justifyContent: 'center',
    alignItems: 'center'
  },
  message: {
    marginTop: spacing.md,
    fontSize: typography.fontSize.md,
    color: colors.text.secondary
  }
});

// ...rest of the code...
