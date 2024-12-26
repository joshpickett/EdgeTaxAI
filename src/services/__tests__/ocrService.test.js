import { processReceipt, captureReceipt, saveReceipt } from '../ocrService';
import { apiClient } from '../apiClient';
import { offlineManager } from '../offlineManager';
import { launchCamera, launchImageLibrary } from 'react-native-image-picker';

jest.mock('../apiClient');
jest.mock('../offlineManager');
jest.mock('react-native-image-picker');

describe('OCRService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    global.navigator.onLine = true;
  });

  describe('processReceipt', () => {
    const mockImageUri = 'file://test.jpg';

    it('processes receipt online successfully', async () => {
      const mockResponse = {
        ok: true,
        data: {
          amount: 50.00,
          date: '2023-01-01',
          vendor: 'Test Store'
        }
      };

      apiClient.post.mockResolvedValueOnce(mockResponse);

      const result = await processReceipt(mockImageUri);
      expect(result).toEqual(mockResponse.data);
      expect(apiClient.post).toHaveBeenCalledWith(
        '/expenses/process-receipt',
        expect.any(FormData),
        expect.any(Object)
      );
    });

    it('queues receipt for offline processing', async () => {
      global.navigator.onLine = false;
      
      await processReceipt(mockImageUri);
      
      expect(offlineManager.queueOperation).toHaveBeenCalledWith({
        type: 'PROCESS_RECEIPT',
        data: expect.any(FormData)
      });
    });

    it('handles processing errors', async () => {
      apiClient.post.mockRejectedValueOnce(new Error('Processing failed'));

      await expect(processReceipt(mockImageUri))
        .rejects
        .toThrow('Processing failed');
    });
  });

  describe('captureReceipt', () => {
    it('launches camera successfully', async () => {
      const mockResult = { assets: [{ uri: 'test.jpg' }] };
      launchCamera.mockResolvedValueOnce(mockResult);

      const result = await captureReceipt({ useCamera: true });
      expect(result).toEqual(mockResult);
      expect(launchCamera).toHaveBeenCalledWith(
        expect.objectContaining({
          mediaType: 'photo',
          includeBase64: true
        })
      );
    });

    it('launches image library successfully', async () => {
      const mockResult = { assets: [{ uri: 'test.jpg' }] };
      launchImageLibrary.mockResolvedValueOnce(mockResult);

      const result = await captureReceipt({ useCamera: false });
      expect(result).toEqual(mockResult);
      expect(launchImageLibrary).toHaveBeenCalled();
    });
  });

  describe('saveReceipt', () => {
    const mockReceiptData = {
      amount: 50.00,
      date: '2023-01-01',
      vendor: 'Test Store'
    };

    it('queues receipt save operation', async () => {
      await saveReceipt(mockReceiptData);

      expect(offlineManager.queueOperation).toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'SAVE_RECEIPT',
          data: mockReceiptData
        })
      );
    });

    it('handles save errors', async () => {
      offlineManager.queueOperation.mockRejectedValueOnce(new Error('Save failed'));

      await expect(saveReceipt(mockReceiptData))
        .rejects
        .toThrow('Save failed');
    });
  });
});
