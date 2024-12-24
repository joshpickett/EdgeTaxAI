import React from 'react';
import { ActivityIndicator, Modal, View, StyleSheet } from 'react-native';

const LoadingOverlay: React.FC<{ isVisible: boolean }> = ({ isVisible }) => {
  return (
    <Modal transparent={true} visible={isVisible}>
      <View style={styles.overlay}>
        <ActivityIndicator size="large" color="#0000ff" />
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
  },
});

export default LoadingOverlay;
