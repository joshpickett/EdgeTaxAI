import { dataSyncService } from '../dataSyncService';
import { apiClient } from '../apiClient';
import { offlineManager } from '../offlineManager';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Platform } from 'react-native';

// Mock dependencies
jest.mock('../apiClient');
jest.mock('../offlineManager');
jest.mock('@react-native-async-storage/async-storage');
jest.mock('react-native', () => ({
  Platform: {
    OS: 'ios'
  }
}));

describe('DataSyncService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Reset sync status
    dataSyncService.syncInProgress = false;
    dataSyncService.lastSyncTime = null;
    
    // Mock navigator.onLine
    Object.defineProperty(global.navigator, 'onLine', {
      writable: true,
      value: true
    });
  });

  describe('startSync', () => {
    it('should not start sync if already in progress', async () => {
      dataSyncService.syncInProgress = true;
      await dataSyncService.startSync();
      expect(apiClient.getExpenses).not.toHaveBeenCalled();
    });

    it('should not sync when offline', async () => {
      global.navigator.onLine = false;
      await dataSyncService.startSync();
      expect(apiClient.getExpenses).not.toHaveBeenCalled();
    });

    it('should sync all data types successfully', async () => {
      const mockExpenses = [{ id: 1, amount: 100 }];
      const mockIncome = [{ id: 1, amount: 1000 }];
      const mockMileage = [{ id: 1, miles: 50 }];

      apiClient.getExpenses.mockResolvedValueOnce(mockExpenses);
      apiClient.getIncome.mockResolvedValueOnce(mockIncome);
      apiClient.getMileage.mockResolvedValueOnce(mockMileage);

      await dataSyncService.startSync();

      expect(dataSyncService.lastSyncTime).toBeTruthy();
      expect(AsyncStorage.setItem).toHaveBeenCalledWith(
        'syncStatus',
        expect.any(String)
      );
    });

    it('should handle sync errors gracefully', async () => {
      apiClient.getExpenses.mockRejectedValueOnce(new Error('Sync failed'));
      
      await expect(dataSyncService.startSync()).rejects.toThrow('Sync failed');
      expect(dataSyncService.syncInProgress).toBeFalsy();
    });
  });

  describe('mergeData', () => {
    it('should merge local and server data correctly', () => {
      const local = [
        { id: 1, amount: 100, lastModified: new Date('2023-01-01') },
        { id: 2, amount: 200, lastModified: new Date('2023-01-02') }
      ];
      const server = [
        { id: 1, amount: 150, lastModified: new Date('2023-01-03') },
        { id: 3, amount: 300, lastModified: new Date('2023-01-01') }
      ];

      const merged = dataSyncService.mergeData(local, server);
      expect(merged).toHaveLength(3);
      expect(merged.find(item => item.id === 1).amount).toBe(150);
    });

    it('should prefer local changes when more recent', () => {
      const local = [{
        id: 1,
        amount: 100,
        lastModified: new Date('2023-01-02')
      }];
      const server = [{
        id: 1,
        amount: 150,
        lastModified: new Date('2023-01-01')
      }];

      const merged = dataSyncService.mergeData(local, server);
      expect(merged[0].amount).toBe(100);
    });
  });

  describe('Receipt Sync', () => {
    it('should upload unsynced receipts', async () => {
      const mockReceipts = [
        { id: 1, synced: false },
        { id: 2, synced: true }
      ];

      offlineManager.getReceipts.mockResolvedValueOnce(mockReceipts);
      await dataSyncService.syncReceipts();

      expect(apiClient.uploadReceipt).toHaveBeenCalledTimes(1);
      expect(apiClient.uploadReceipt).toHaveBeenCalledWith(mockReceipts[0]);
    });
  });

  describe('Sync Status', () => {
    it('should update sync status after successful sync', async () => {
      await dataSyncService.updateSyncStatus();
      
      expect(AsyncStorage.setItem).toHaveBeenCalledWith(
        'syncStatus',
        expect.stringContaining('platform')
      );
    });

    it('should retrieve sync status correctly', async () => {
      const mockStatus = {
        lastSync: new Date().toISOString(),
        platform: 'ios',
        version: '1.0'
      };

      AsyncStorage.getItem.mockResolvedValueOnce(JSON.stringify(mockStatus));
      const status = await dataSyncService.getSyncStatus();

      expect(status).toEqual(mockStatus);
    });
  });

  describe('Error Handling', () => {
    it('should handle AsyncStorage errors', async () => {
      AsyncStorage.setItem.mockRejectedValueOnce(new Error('Storage error'));
      
      await expect(dataSyncService.updateSyncStatus())
        .rejects.toThrow('Storage error');
    });

    it('should handle API errors during sync', async () => {
      apiClient.getExpenses.mockRejectedValueOnce(new Error('API error'));
      
      await expect(dataSyncService.syncExpenses())
        .rejects.toThrow('API error');
    });
  });
});
