import { syncService } from '../syncService';
import { offlineManager } from '../offlineManager';
import { apiClient } from '../apiClient';
import NetInfo from '@react-native-community/netinfo';

// Mock dependencies
jest.mock('../offlineManager');
jest.mock('../apiClient');
jest.mock('@react-native-community/netinfo');

describe('SyncService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    syncService.syncInProgress = false;
    syncService.lastSyncTime = null;

    // Mock NetInfo default response
    NetInfo.fetch.mockResolvedValue({ isConnected: true });
  });

  describe('syncData', () => {
    it('should not start sync if already in progress', async () => {
      syncService.syncInProgress = true;
      await syncService.syncData();
      expect(NetInfo.fetch).not.toHaveBeenCalled();
    });

    it('should handle offline state', async () => {
      NetInfo.fetch.mockResolvedValueOnce({ isConnected: false });
      await expect(syncService.syncData()).rejects.toThrow('No internet connection');
    });

    it('should sync all data types successfully', async () => {
      // Mock successful sync operations
      jest.spyOn(syncService, 'syncExpenses').mockResolvedValueOnce();
      jest.spyOn(syncService, 'syncMileage').mockResolvedValueOnce();
      jest.spyOn(syncService, 'syncReceipts').mockResolvedValueOnce();

      await syncService.syncData();

      expect(syncService.syncExpenses).toHaveBeenCalled();
      expect(syncService.syncMileage).toHaveBeenCalled();
      expect(syncService.syncReceipts).toHaveBeenCalled();
      expect(syncService.lastSyncTime).toBeTruthy();
    });

    it('should handle sync errors', async () => {
      jest.spyOn(syncService, 'syncExpenses')
        .mockRejectedValueOnce(new Error('Sync failed'));

      await expect(syncService.syncData()).rejects.toThrow('Sync failed');
      expect(syncService.syncInProgress).toBe(false);
    });
  });

  describe('syncExpenses', () => {
    const mockLocalExpenses = [
      { id: 1, amount: 100, lastModified: new Date('2023-01-01') }
    ];
    const mockServerExpenses = [
      { id: 1, amount: 150, lastModified: new Date('2023-01-02') }
    ];

    beforeEach(() => {
      jest.spyOn(syncService, 'getLocalExpenses')
        .mockResolvedValue(mockLocalExpenses);
      apiClient.getExpenses.mockResolvedValue(mockServerExpenses);
    });

    it('should merge and update expenses correctly', async () => {
      await syncService.syncExpenses();

      expect(syncService.updateLocalExpenses)
        .toHaveBeenCalledWith(expect.arrayContaining([
          expect.objectContaining({ amount: 150 })
        ]));
      expect(apiClient.updateExpenses).toHaveBeenCalled();
    });

    it('should handle merge conflicts', async () => {
      const conflictingLocal = [
        { id: 1, amount: 200, lastModified: new Date('2023-01-03') }
      ];
      jest.spyOn(syncService, 'getLocalExpenses')
        .mockResolvedValueOnce(conflictingLocal);

      await syncService.syncExpenses();

      expect(syncService.updateLocalExpenses)
        .toHaveBeenCalledWith(expect.arrayContaining([
          expect.objectContaining({ amount: 200 })
        ]));
    });
  });

  describe('syncMileage', () => {
    const mockLocalMileage = [
      { id: 1, miles: 50, lastModified: new Date('2023-01-01') }
    ];
    const mockServerMileage = [
      { id: 1, miles: 75, lastModified: new Date('2023-01-02') }
    ];

    beforeEach(() => {
      jest.spyOn(syncService, 'getLocalMileage')
        .mockResolvedValue(mockLocalMileage);
      apiClient.getMileage.mockResolvedValue(mockServerMileage);
    });

    it('should merge and update mileage records correctly', async () => {
      await syncService.syncMileage();

      expect(syncService.updateLocalMileage)
        .toHaveBeenCalledWith(expect.arrayContaining([
          expect.objectContaining({ miles: 75 })
        ]));
      expect(apiClient.updateMileage).toHaveBeenCalled();
    });
  });

  describe('syncReceipts', () => {
    const mockLocalReceipts = [
      { id: 1, synced: false },
      { id: 2, synced: true }
    ];

    beforeEach(() => {
      jest.spyOn(syncService, 'getLocalReceipts')
        .mockResolvedValue(mockLocalReceipts);
    });

    it('should only upload unsynced receipts', async () => {
      await syncService.syncReceipts();

      expect(syncService.uploadReceipt)
        .toHaveBeenCalledTimes(1);
      expect(syncService.uploadReceipt)
        .toHaveBeenCalledWith(expect.objectContaining({ id: 1 }));
    });
  });

  describe('Merge Logic', () => {
    describe('mergeExpenses', () => {
      it('should prefer newer local changes', () => {
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

        const result = syncService.mergeExpenses(local, server);
        expect(result[0].amount).toBe(100);
      });

      it('should handle missing local entries', () => {
        const local = [];
        const server = [{
          id: 1,
          amount: 150,
          lastModified: new Date('2023-01-01')
        }];

        const result = syncService.mergeExpenses(local, server);
        expect(result).toEqual(server);
      });
    });

    describe('mergeMileage', () => {
      it('should prefer newer server changes', () => {
        const local = [{
          id: 1,
          miles: 50,
          lastModified: new Date('2023-01-01')
        }];
        const server = [{
          id: 1,
          miles: 75,
          lastModified: new Date('2023-01-02')
        }];

        const result = syncService.mergeMileage(local, server);
        expect(result[0].miles).toBe(75);
      });
    });
  });
});
