import React from 'react';
import { View, ActivityIndicator, Platform, StyleSheet } from 'react-native';
import { colors, spacing } from '../styles/tokens';

const LoadingState = ({ size = 'large', color = colors.primary.main }) => {
  const getLoadingIndicator = () => {
    if (Platform.OS === 'ios') {
      return (
        <ActivityIndicator
          size={size}
          color={color}
          style={styles.indicator}
        />
      );
    }

    // Android-specific loading indicator
    return (
      <ActivityIndicator
        size={size}
        color={color}
        style={[styles.indicator, styles.androidIndicator]}
      />
    );
  };

  return (
    <View style={styles.container}>
      {getLoadingIndicator()}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: spacing.lg
  },
  indicator: {
    margin: spacing.md
  },
  androidIndicator: {
    transform: [{ scale: 1.2 }] // Slightly larger on Android
  }
});

export default LoadingState;
