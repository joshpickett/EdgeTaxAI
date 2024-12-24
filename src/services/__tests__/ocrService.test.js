import { processReceipt, captureReceipt, saveReceipt } from '../ocrService';
import { apiClient } from '../apiClient';
import { offlineManager } from '../offlineManager';
import { launchCamera, launchImageLibrary } from 'react-native-image-picker';

// Mock dependencies
jest.mock('../apiClient');
jest.mock('../offlineManager');
jest.mock('react-native-image-picker');

describe('OCR Service', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Reset navigator.onLine
    Object.defineProperty(global.navigator, 'onLine', {
      writable: true,
      value: true
    });
    // Mock FormData
    global.FormData = jest.fn(() => ({
      append: jest.fn()
    }));
  });

  describe('processReceipt', () => {
    const mockImageUri = 'file://test/image.jpg';

    it('should process receipt online successfully', async () => {
      const mockResponse = {
        ok: true,
        data: {
          total: 100,
          date: '2023-01-01',
          vendor: 'Test Store'
        }
      };
      apiClient.post.mockResolvedValueOnce(mockResponse);

      const result = await processReceipt(mockImageUri);
      expect(result).toEqual(mockResponse.data);
      expect(apiClient.post).toHaveBeenCalledWith(
        '/process-receipt',
        expect.any(FormData),
        expect.any(Object)
      );
    });

    it('should queue receipt for offline processing', async () => {
      Object.defineProperty(global.navigator, 'onLine', { value: false });
      
      const result = await processReceipt(mockImageUri);
      expect(result).toBeNull();
      expect(offlineManager.queueOperation).toHaveBeenCalledWith({
        type: 'PROCESS_RECEIPT',
        data: expect.any(FormData)
      });
    });

    it('should handle processing errors', async () => {
      apiClient.post.mockRejectedValueOnce(new Error('Processing failed'));
      
      await expect(processReceipt(mockImageUri))
        .rejects.toThrow('Processing failed');
      expect(console.error).toHaveBeenCalled();
    });
  });

  describe('captureReceipt', () => {
    const defaultOptions = {
      mediaType: 'photo',
      includeBase64: true,
      quality: 0.8,
    };

    it('should launch camera when useCamera is true', async () => {
      const mockResult = { assets: [{ uri: 'test-uri' }] };
      launchCamera.mockResolvedValueOnce(mockResult);

      const result = await captureReceipt({ useCamera: true });
      expect(result).toEqual(mockResult);
      expect(launchCamera).toHaveBeenCalledWith({
        ...defaultOptions,
        useCamera: true
      });
    });

    it('should launch image library when useCamera is false', async () => {
      const mockResult = { assets: [{ uri: 'test-uri' }] };
      launchImageLibrary.mockResolvedValueOnce(mockResult);

      const result = await captureReceipt({ useCamera: false });
      expect(result).toEqual(mockResult);
      expect(launchImageLibrary).toHaveBeenCalledWith({
        ...defaultOptions,
        useCamera: false
      });
    });

    it('should handle camera/library errors', async () => {
      launchCamera.mockRejectedValueOnce(new Error('Camera error'));
      
      await expect(captureReceipt({ useCamera: true }))
        .rejects.toThrow('Camera error');
      expect(console.error).toHaveBeenCalled();
    });
  });

  describe('saveReceipt', () => {
    const mockReceiptData = {
      total: 100,
      date: '2023-01-01',
      vendor: 'Test Store'
    };

    it('should queue receipt save operation', async () => {
      const result = await saveReceipt(mockReceiptData);
      
      expect(result).toBe(true);
      expect(offlineManager.queueOperation).toHaveBeenCalledWith({
        type: 'SAVE_RECEIPT',
        data: mockReceiptData,
        execute: expect.any(Function)
      });
    });

    it('should handle save errors', async () => {
      offlineManager.queueOperation.mockRejectedValueOnce(
        new Error('Save failed')
      );
      
      await expect(saveReceipt(mockReceiptData))
        .rejects.toThrow('Save failed');
      expect(console.error).toHaveBeenCalled();
    });

    it('should execute save operation correctly', async () => {
      await saveReceipt(mockReceiptData);
      
      // Get the execute function from the queued operation
      const operation = offlineManager.queueOperation.mock.calls[0][0];
      await operation.execute();
      
      expect(apiClient.post).toHaveBeenCalledWith(
        '/receipts',
        mockReceiptData
      );
    });
  });
});
