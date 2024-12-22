import React from 'react';
import { View, ActivityIndicator, Platform, StyleSheet, Text } from 'react-native';
import { colors, spacing } from '../styles/tokens';

const LoadingState = ({ 
  size = 'large', 
  color = colors.primary.main,
  message = 'Loading...',
  fullScreen = false 
}) => {
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
    <View style={[styles.container, fullScreen && styles.fullScreen]}>
      {getLoadingIndicator()}
      {message && (
        <Text style={styles.message}>{message}</Text>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: spacing.lg,
    backgroundColor: 'transparent'
  },
  fullScreen: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(255, 255, 255, 0.8)'
  },
  indicator: {
    margin: spacing.md
  },
  androidIndicator: {
    transform: [{ scale: 1.2 }] // Slightly larger on Android
  },
  message: {
    marginTop: spacing.md,
    color: colors.text.secondary
  }
});

export default LoadingState;
