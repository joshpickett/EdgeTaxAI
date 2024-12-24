import { offlineManager } from '../offlineManager';
import AsyncStorage from '@react-native-async-storage/async-storage';
import NetInfo from '@react-native-community/netinfo';
import { apiClient } from '../apiClient';

// Mock dependencies
jest.mock('@react-native-async-storage/async-storage');
jest.mock('@react-native-community/netinfo');
jest.mock('../apiClient');

describe('OfflineManager', () => {
  let netInfoCallback;

  beforeEach(() => {
    jest.clearAllMocks();
    offlineManager.syncQueue = [];
    offlineManager.isOnline = true;

    // Mock NetInfo event listener
    NetInfo.addEventListener.mockImplementation(callback => {
      netInfoCallback = callback;
      return () => {};
    });
  });

  describe('Network State Management', () => {
    it('should initialize with correct default values', () => {
      expect(offlineManager.syncQueue).toEqual([]);
      expect(offlineManager.isOnline).toBe(true);
      expect(NetInfo.addEventListener).toHaveBeenCalled();
    });

    it('should handle network state changes', () => {
      netInfoCallback({ isConnected: false });
      expect(offlineManager.isOnline).toBe(false);

      netInfoCallback({ isConnected: true });
      expect(offlineManager.isOnline).toBe(true);
    });

    it('should process queue when coming online', async () => {
      const processSyncQueueSpy = jest.spyOn(offlineManager, 'processSyncQueue');
      
      offlineManager.isOnline = false;
      netInfoCallback({ isConnected: true });

      expect(processSyncQueueSpy).toHaveBeenCalled();
    });
  });

  describe('Queue Operations', () => {
    const mockOperation = {
      type: 'PROCESS_RECEIPT',
      data: { receiptId: '123' }
    };

    it('should queue operation successfully', async () => {
      await offlineManager.queueOperation(mockOperation);

      expect(offlineManager.syncQueue).toContain(mockOperation);
      expect(AsyncStorage.setItem).toHaveBeenCalledWith(
        'syncQueue',
        JSON.stringify([mockOperation])
      );
    });

    it('should process queue immediately if online', async () => {
      const processSyncQueueSpy = jest.spyOn(offlineManager, 'processSyncQueue');
      offlineManager.isOnline = true;

      await offlineManager.queueOperation(mockOperation);

      expect(processSyncQueueSpy).toHaveBeenCalled();
    });

    it('should handle queueing errors', async () => {
      AsyncStorage.setItem.mockRejectedValueOnce(new Error('Storage error'));
      console.error = jest.fn();

      await offlineManager.queueOperation(mockOperation);

      expect(console.error).toHaveBeenCalled();
    });
  });

  describe('Operation Handlers', () => {
    it('should handle receipt processing', async () => {
      const mockData = { receiptId: '123' };
      const mockResponse = { processed: true };
      
      apiClient.post.mockResolvedValueOnce({ data: mockResponse });

      const result = await offlineManager.handleReceiptProcessing({
        type: 'PROCESS_RECEIPT',
        data: mockData
      });

      expect(result).toEqual(mockResponse);
      expect(apiClient.post).toHaveBeenCalledWith('/process-receipt', mockData);
    });

    it('should handle receipt saving', async () => {
      const mockData = { receipt: 'data' };
      
      await offlineManager.handleReceiptSaving({
        type: 'SAVE_RECEIPT',
        data: mockData
      });

      expect(apiClient.post).toHaveBeenCalledWith('/receipts', mockData);
    });
  });

  describe('Queue Processing', () => {
    it('should process queue items in order', async () => {
      const mockOperations = [
        { type: 'PROCESS_RECEIPT', data: { id: 1 } },
        { type: 'SAVE_RECEIPT', data: { id: 2 } }
      ];

      offlineManager.syncQueue = [...mockOperations];
      apiClient.post.mockResolvedValueOnce({ data: { processed: true } })
                   .mockResolvedValueOnce({ data: { saved: true } });

      await offlineManager.processSyncQueue();

      expect(AsyncStorage.setItem).toHaveBeenCalledWith('syncQueue', '[]');
      expect(offlineManager.syncQueue).toHaveLength(0);
    });

    it('should stop processing on error', async () => {
      const mockOperations = [
        { type: 'PROCESS_RECEIPT', data: { id: 1 } },
        { type: 'SAVE_RECEIPT', data: { id: 2 } }
      ];

      offlineManager.syncQueue = [...mockOperations];
      apiClient.post.mockRejectedValueOnce(new Error('Processing failed'));

      await offlineManager.processSyncQueue();

      expect(offlineManager.syncQueue).toHaveLength(2);
      expect(console.error).toHaveBeenCalled();
    });
  });

  describe('Queue Persistence', () => {
    it('should load sync queue from storage on init', async () => {
      const mockQueue = [{ type: 'PROCESS_RECEIPT', data: { id: 1 } }];
      AsyncStorage.getItem.mockResolvedValueOnce(JSON.stringify(mockQueue));

      await offlineManager.loadSyncQueue();

      expect(offlineManager.syncQueue).toEqual(mockQueue);
    });

    it('should handle storage errors when loading queue', async () => {
      AsyncStorage.getItem.mockRejectedValueOnce(new Error('Storage error'));
      console.error = jest.fn();

      await offlineManager.loadSyncQueue();

      expect(console.error).toHaveBeenCalled();
      expect(offlineManager.syncQueue).toEqual([]);
    });
  });

  describe('Edge Cases', () => {
    it('should handle invalid operation types', async () => {
      const invalidOperation = {
        type: 'INVALID_TYPE',
        data: {}
      };

      await offlineManager.queueOperation(invalidOperation);
      await offlineManager.processSyncQueue();

      expect(console.error).toHaveBeenCalled();
    });

    it('should handle empty queue processing', async () => {
      offlineManager.syncQueue = [];
      await offlineManager.processSyncQueue();

      expect(AsyncStorage.setItem).not.toHaveBeenCalled();
    });

    it('should handle null data in operations', async () => {
      const nullDataOperation = {
        type: 'PROCESS_RECEIPT',
        data: null
      };

      await offlineManager.queueOperation(nullDataOperation);
      await offlineManager.processSyncQueue();

      expect(console.error).toHaveBeenCalled();
    });
  });
});
