import { syncService } from '../syncService';
import { apiClient } from '../apiClient';
import NetInfo from '@react-native-community/netinfo';

jest.mock('../apiClient');
jest.mock('@react-native-community/netinfo');

describe('SyncService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    NetInfo.fetch.mockResolvedValue({ isConnected: true });
  });

  describe('syncData', () => {
    it('syncs all data types when online', async () => {
      const mockExpenses = [{ id: 1 }];
      const mockMileage = [{ id: 1 }];
      
      apiClient.getExpenses.mockResolvedValueOnce(mockExpenses);
      apiClient.getMileage.mockResolvedValueOnce(mockMileage);

      await syncService.syncData();

      expect(apiClient.getExpenses).toHaveBeenCalled();
      expect(apiClient.getMileage).toHaveBeenCalled();
    });

    it('handles offline state', async () => {
      NetInfo.fetch.mockResolvedValueOnce({ isConnected: false });
      
      await expect(syncService.syncData()).rejects.toThrow('No internet connection');
    });

    it('prevents concurrent syncs', async () => {
      syncService.syncInProgress = true;
      const result = await syncService.syncData();
      expect(result).toBeUndefined();
    });
  });

  describe('mergeExpenses', () => {
    it('correctly merges local and server expenses', () => {
      const local = [
        { id: 1, amount: 100, lastModified: new Date('2023-01-01') }
      ];
      const server = [
        { id: 1, amount: 200, lastModified: new Date('2023-01-02') }
      ];

      const result = syncService.mergeExpenses(local, server);
      expect(result[0].amount).toBe(200);
    });
  });

  describe('syncReceipts', () => {
    it('uploads unsynced receipts', async () => {
      const mockReceipts = [
        { id: 1, synced: false },
        { id: 2, synced: true }
      ];

      jest.spyOn(syncService, 'getLocalReceipts')
        .mockResolvedValueOnce(mockReceipts);

      await syncService.syncReceipts();
      expect(syncService.uploadReceipt).toHaveBeenCalledTimes(1);
    });
  });
});
