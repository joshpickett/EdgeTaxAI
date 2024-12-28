import React from 'react';
import { View, ActivityIndicator, StyleSheet } from 'react-native';
import { setupSrcPath } from '../setup_path';
import { colors } from '../styles/tokens';
setupSrcPath();

interface LoadingOverlayProps {
  color?: string;
  size?: 'small' | 'large';
}

const LoadingOverlay: React.FC<LoadingOverlayProps> = ({ 
  color = colors.primary.main,
  size = 'large'
}) => {
  return (
    <View style={styles.container} testID="loading-overlay">
      <View style={styles.overlay}>
        <ActivityIndicator size={size} color={color} />
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: colors.overlay,
    zIndex: 1000,
    justifyContent: 'center',
    alignItems: 'center',
  },
  overlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.3)',
    justifyContent: 'center',
    alignItems: 'center',
  },
});

export default LoadingOverlay;
