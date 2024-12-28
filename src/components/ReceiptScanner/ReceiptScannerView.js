import React, { useState } from 'react';
import { View, Image, StyleSheet, Alert, Text } from 'react-native';
import { setupSrcPath } from '../../setup_path';
import { Camera } from 'expo-camera';
import CustomButton from '../CustomButton';
import { colors, typography, spacing } from '../../styles/tokens';
import { receiptScanner } from '../../services/receiptScanner';
import { handleError } from '../../utils/errorHandler';

const ReceiptScannerView = ({ onScanComplete }) => {
  const [hasPermission, setHasPermission] = useState(null);
  const [scannedImage, setScannedImage] = useState(null);
  const [loading, setLoading] = useState(false);

  React.useEffect(() => {
    (async () => {
      const { status } = await Camera.requestCameraPermissionsAsync();
      setHasPermission(status === 'granted');
    })();
  }, []);

  const handleScan = async () => {
    try {
      setLoading(true);
      const result = await receiptScanner.scanReceipt({ useCamera: true });
      
      if (result) {
        setScannedImage(result.uri);
        onScanComplete?.(result);
      }
    } catch (error) {
      const appError = handleError(error, 'ReceiptScanner');
      Alert.alert('Error', appError.message);
    } finally {
      setLoading(false);
    }
  };

  if (hasPermission === null) {
    return <View />;
  }

  if (hasPermission === false) {
    return <Text>No access to camera</Text>;
  }

  return (
    <View style={styles.container}>
      {scannedImage ? (
        <Image source={{ uri: scannedImage }} style={styles.preview} />
      ) : (
        <Camera style={styles.camera} />
      )}
      <CustomButton
        title={scannedImage ? "Scan Another" : "Scan Receipt"}
        onPress={handleScan}
        loading={loading}
        style={styles.button}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: spacing.md,
  },
  camera: {
    flex: 1,
  },
  preview: {
    width: '100%',
    height: 300,
    borderRadius: spacing.sm,
    resizeMode: 'contain',
  },
  button: {
    margin: spacing.md,
    backgroundColor: colors.primary.main,
  },
});

export default ReceiptScannerView;
