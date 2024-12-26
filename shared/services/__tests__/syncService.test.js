import SyncService from '../syncService';
import { apiClient } from '../apiClient';
import { SYNC_STATES } from '../../constants';

jest.mock('../apiClient');

describe('SyncService', () => {
    let syncService;
    let mockSubscriber;

    beforeEach(() => {
        syncService = new SyncService();
        mockSubscriber = jest.fn();
        jest.clearAllMocks();
    });

    describe('syncData', () => {
        const userId = '123';

        test('should sync data successfully', async () => {
            apiClient.get.mockResolvedValue({ data: { status: 'success' } });
            
            const result = await syncService.syncData(userId);
            expect(result.status).toBe(SYNC_STATES.COMPLETED);
            expect(result.lastSync).toBeInstanceOf(Date);
        });

        test('should prevent concurrent syncs', async () => {
            syncService.syncInProgress = true;
            const result = await syncService.syncData(userId);
            expect(result.status).toBe(SYNC_STATES.SYNCING);
        });

        test('should handle sync errors', async () => {
            apiClient.get.mockRejectedValue(new Error('Sync failed'));
            
            const result = await syncService.syncData(userId);
            expect(result.status).toBe(SYNC_STATES.ERROR);
            expect(result.error).toBeDefined();
        });
    });

    describe('subscribeSyncStatus', () => {
        test('should add and remove subscribers', () => {
            const unsubscribe = syncService.subscribeSyncStatus(mockSubscriber);
            expect(syncService.statusSubscribers.size).toBe(1);
            
            unsubscribe();
            expect(syncService.statusSubscribers.size).toBe(0);
        });

        test('should notify subscribers of status changes', async () => {
            syncService.subscribeSyncStatus(mockSubscriber);
            await syncService.syncData('123');
            
            expect(mockSubscriber).toHaveBeenCalledWith(
                expect.objectContaining({ status: SYNC_STATES.SYNCING })
            );
            expect(mockSubscriber).toHaveBeenCalledWith(
                expect.objectContaining({ status: SYNC_STATES.COMPLETED })
            );
        });
    });

    describe('getSyncStatus', () => {
        test('should fetch sync status successfully', async () => {
            const mockStatus = { lastSync: new Date().toISOString() };
            apiClient.get.mockResolvedValueOnce({ data: mockStatus });

            const result = await syncService.getSyncStatus('123');
            expect(result).toEqual(mockStatus);
        });

        test('should handle status fetch errors', async () => {
            apiClient.get.mockRejectedValueOnce(new Error('Failed to fetch status'));
            
            await expect(syncService.getSyncStatus('123'))
                .rejects.toThrow('Failed to fetch status');
        });
    });
});
