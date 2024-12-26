import { dataSyncService } from '../dataSyncService';
import { apiClient } from '../apiClient';
import { offlineManager } from '../offlineManager';
import AsyncStorage from '@react-native-async-storage/async-storage';

jest.mock('../apiClient');
jest.mock('../offlineManager');
jest.mock('@react-native-async-storage/async-storage');

describe('DataSyncService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    global.navigator.onLine = true;
  });

  describe('startSync', () => {
    it('successfully syncs all data types', async () => {
      const mockExpenses = [{ id: 1, amount: 100 }];
      const mockIncome = [{ id: 1, amount: 1000 }];
      
      apiClient.getExpenses.mockResolvedValueOnce(mockExpenses);
      apiClient.getIncome.mockResolvedValueOnce(mockIncome);
      
      await dataSyncService.startSync();
      
      expect(AsyncStorage.setItem).toHaveBeenCalledWith(
        'syncStatus',
        expect.any(String)
      );
    });

    it('handles offline state', async () => {
      global.navigator.onLine = false;
      await dataSyncService.startSync();
      expect(apiClient.getExpenses).not.toHaveBeenCalled();
    });

    it('handles sync errors', async () => {
      apiClient.getExpenses.mockRejectedValueOnce(new Error('Sync failed'));
      await expect(dataSyncService.startSync()).rejects.toThrow('Sync failed');
    });
  });

  describe('syncExpenses', () => {
    it('successfully syncs expenses', async () => {
      const localExpenses = [{ id: 1, amount: 100 }];
      const serverExpenses = [{ id: 2, amount: 200 }];
      
      offlineManager.getExpenses.mockResolvedValueOnce(localExpenses);
      apiClient.getExpenses.mockResolvedValueOnce(serverExpenses);
      
      await dataSyncService.syncExpenses();
      
      expect(AsyncStorage.setItem).toHaveBeenCalledWith(
        'lastExpenseSync',
        expect.any(String)
      );
    });

    it('handles merge conflicts', async () => {
      const localExpenses = [{ id: 1, amount: 100, lastModified: new Date() }];
      const serverExpenses = [{ id: 1, amount: 200, lastModified: new Date(Date.now() - 1000) }];
      
      offlineManager.getExpenses.mockResolvedValueOnce(localExpenses);
      apiClient.getExpenses.mockResolvedValueOnce(serverExpenses);
      
      await dataSyncService.syncExpenses();
      
      expect(apiClient.updateExpenses).toHaveBeenCalledWith(
        expect.arrayContaining([expect.objectContaining({ amount: 100 })])
      );
    });
  });

  describe('checkPendingOperations', () => {
    it('executes pending operations', async () => {
      const mockOperation = {
        id: '1',
        execute: jest.fn().mockResolvedValueOnce(true)
      };
      
      offlineManager.getPendingOperations.mockResolvedValueOnce([mockOperation]);
      
      await dataSyncService.checkPendingOperations();
      
      expect(mockOperation.execute).toHaveBeenCalled();
      expect(offlineManager.removeOperation).toHaveBeenCalledWith('1');
    });

    it('handles operation execution errors', async () => {
      const mockOperation = {
        id: '1',
        execute: jest.fn().mockRejectedValueOnce(new Error('Operation failed'))
      };
      
      offlineManager.getPendingOperations.mockResolvedValueOnce([mockOperation]);
      
      await dataSyncService.checkPendingOperations();
      
      expect(mockOperation.execute).toHaveBeenCalled();
      expect(offlineManager.removeOperation).not.toHaveBeenCalled();
    });
  });
});
