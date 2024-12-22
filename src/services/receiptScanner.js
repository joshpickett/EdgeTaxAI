import { Platform } from 'react-native';
import { launchCamera, launchImageLibrary } from 'react-native-image-picker';
import { apiClient } from './apiClient';
import { offlineManager } from './offlineManager';

class ReceiptScanner {
  async scanReceipt(options = {}) {
    try {
      const imageResponse = await this.captureImage(options);
      if (imageResponse.didCancel) {
        return null;
      }

      const receipt = imageResponse.assets[0];
      const scannedData = await this.processReceipt(receipt);
      
      return scannedData;
    } catch (error) {
      console.error('Error scanning receipt:', error);
      throw error;
    }
  }

  async captureImage(options = {}) {
    const defaultOptions = {
      mediaType: 'photo',
      includeBase64: true,
      quality: 0.8,
    };

    try {
      if (options.useCamera) {
        return await launchCamera({ ...defaultOptions, ...options });
      } else {
        return await launchImageLibrary({ ...defaultOptions, ...options });
      }
    } catch (error) {
      console.error('Error capturing image:', error);
      throw error;
    }
  }

  async processReceipt(receipt) {
    try {
      const formData = new FormData();
      formData.append('receipt', {
        uri: receipt.uri,
        type: receipt.type,
        name: receipt.fileName,
      });

      const response = await apiClient.post('/receipts/scan', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      return response.data;
    } catch (error) {
      console.error('Error processing receipt:', error);
      throw error;
    }
  }

  async saveReceipt(receiptData) {
    try {
      const operation = {
        execute: async () => {
          await apiClient.post('/receipts', receiptData);
        },
      };

      await offlineManager.queueOperation(operation);
      return true;
    } catch (error) {
      console.error('Error saving receipt:', error);
      throw error;
    }
  }
}

export const receiptScanner = new ReceiptScanner();
