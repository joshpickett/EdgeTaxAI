//deprecated
import { apiClient } from './apiClient';
import { offlineManager } from './offlineManager';
import { Platform } from 'react-native';
import { launchCamera, launchImageLibrary } from 'react-native-image-picker';

export const processReceipt = async (imageUri) => {
  try {
    const formData = new FormData();
    formData.append('receipt', {
      uri: imageUri,
      type: 'image/jpeg',
      name: 'receipt.jpg',
    });

    // Try online processing first
    if (navigator.onLine) {
      const response = await apiClient.post('/expenses/process-receipt', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      if (!response.ok) {
        throw new Error('Failed to process receipt');
      }
      
      return formatReceiptData(response.data);
    } else {
      // Queue for offline processing
      await offlineManager.queueOperation({
        type: 'PROCESS_RECEIPT',
        data: formData
      });
      return null;
    }
  } catch (error) {
    console.error('Receipt processing error:', error);
    throw error;
  }
};

export const captureReceipt = async (options = {}) => {
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
};

export const saveReceipt = async (receiptData) => {
  try {
    const operation = {
      type: 'SAVE_RECEIPT',
      data: receiptData,
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
};

// ...rest of the code...
