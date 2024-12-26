import { offlineManager } from '../offlineManager';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { dataSyncService } from '../dataSyncService';

jest.mock('@react-native-async-storage/async-storage');
jest.mock('../dataSyncService');

describe('OfflineManager', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    offlineManager.operationQueue = [];
  });

  describe('createOperation', () => {
    it('creates operation with correct structure', () => {
      const operationData = {
        type: 'TEST_OPERATION',
        data: { test: 'data' }
      };

      const operation = offlineManager.createOperation(operationData);

      expect(operation).toMatchObject({
        id: expect.any(String),
        timestamp: expect.any(String),
        retryCount: 0,
        ...operationData
      });
    });
  });

  describe('queueOperation', () => {
    it('queues operation successfully', async () => {
      const operation = {
        type: 'TEST_OPERATION',
        data: { test: 'data' }
      };

      await offlineManager.queueOperation(operation);

      expect(AsyncStorage.setItem).toHaveBeenCalledWith(
        expect.any(String),
        expect.any(String)
      );
    });

    it('handles operation queue limit', async () => {
      const operations = Array(11).fill({
        type: 'TEST_OPERATION',
        data: { test: 'data' }
      });

      for (const operation of operations) {
        await offlineManager.queueOperation(operation);
      }

      expect(offlineManager.operationQueue.length).toBeLessThanOrEqual(10);
    });
  });

  describe('retryOperation', () => {
    it('retries operation successfully', async () => {
      const operation = {
        id: '1',
        type: 'TEST_OPERATION',
        retryCount: 0,
        execute: jest.fn().mockResolvedValueOnce(true)
      };

      const result = await offlineManager.retryOperation(operation);
      expect(result).toBe(true);
      expect(operation.execute).toHaveBeenCalled();
    });

    it('handles max retries', async () => {
      const operation = {
        id: '1',
        type: 'TEST_OPERATION',
        retryCount: 3,
        execute: jest.fn()
      };

      const result = await offlineManager.retryOperation(operation);
      expect(result).toBe(false);
      expect(operation.execute).not.toHaveBeenCalled();
    });
  });

  describe('processQueue', () => {
    it('processes queued operations', async () => {
      const operations = [
        {
          id: '1',
          execute: jest.fn().mockResolvedValueOnce(true)
        },
        {
          id: '2',
          execute: jest.fn().mockResolvedValueOnce(true)
        }
      ];

      offlineManager.operationQueue = operations;
      await offlineManager.processQueue();

      operations.forEach(op => {
        expect(op.execute).toHaveBeenCalled();
      });
    });

    it('handles failed operations', async () => {
      const failedOperation = {
        id: '1',
        execute: jest.fn().mockRejectedValueOnce(new Error('Failed'))
      };

      offlineManager.operationQueue = [failedOperation];
      await offlineManager.processQueue();

      expect(failedOperation.execute).toHaveBeenCalled();
      expect(offlineManager.operationQueue).toContain(failedOperation);
    });
  });
});
