import { receiptScanner } from '../receiptScanner';
import { launchCamera, launchImageLibrary } from 'react-native-image-picker';
import { apiClient } from '../apiClient';
import { offlineManager } from '../offlineManager';

jest.mock('react-native-image-picker');
jest.mock('../apiClient');
jest.mock('../offlineManager');

describe('ReceiptScanner', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('scanReceipt', () => {
    it('captures and processes receipt successfully', async () => {
      const mockImageResponse = {
        assets: [{
          uri: 'test-uri',
          type: 'image/jpeg',
          fileName: 'test.jpg'
        }]
      };

      const mockProcessedData = {
        amount: 50.00,
        vendor: 'Test Store',
        date: '2023-01-01'
      };

      launchCamera.mockResolvedValueOnce(mockImageResponse);
      apiClient.post.mockResolvedValueOnce({ data: mockProcessedData });

      const result = await receiptScanner.scanReceipt({ useCamera: true });
      expect(result).toEqual(mockProcessedData);
    });

    it('handles cancelled image capture', async () => {
      launchCamera.mockResolvedValueOnce({ didCancel: true });
      const result = await receiptScanner.scanReceipt({ useCamera: true });
      expect(result).toBeNull();
    });

    it('handles processing errors', async () => {
      const mockImageResponse = {
        assets: [{
          uri: 'test-uri',
          type: 'image/jpeg',
          fileName: 'test.jpg'
        }]
      };

      launchCamera.mockResolvedValueOnce(mockImageResponse);
      apiClient.post.mockRejectedValueOnce(new Error('Processing failed'));

      await expect(receiptScanner.scanReceipt({ useCamera: true }))
        .rejects.toThrow('Processing failed');
    });
  });

  describe('saveReceipt', () => {
    it('queues receipt save operation', async () => {
      const receiptData = {
        amount: 50.00,
        vendor: 'Test Store',
        date: '2023-01-01'
      };

      await receiptScanner.saveReceipt(receiptData);

      expect(offlineManager.queueOperation).toHaveBeenCalledWith(
        expect.objectContaining({
          execute: expect.any(Function)
        })
      );
    });

    it('handles save errors', async () => {
      const receiptData = {
        amount: 50.00,
        vendor: 'Test Store',
        date: '2023-01-01'
      };

      offlineManager.queueOperation.mockRejectedValueOnce(new Error('Save failed'));

      await expect(receiptScanner.saveReceipt(receiptData))
        .rejects.toThrow('Save failed');
    });
  });
});
