import { apiClient } from './apiClient';
import { handleApiError } from '../utils/errorHandler';
import { SYNC_STATES } from '../constants';

class SyncService {
    constructor() {
        this.syncInProgress = false;
        this.lastSyncTime = null;
        this.syncQueue = [];
        this.statusSubscribers = new Set();
    }

    async syncData(userId) {
        if (this.syncInProgress) {
            return { status: SYNC_STATES.SYNCING };
        }

        try {
            this.syncInProgress = true;
            this.notifySubscribers({ status: SYNC_STATES.SYNCING });
            
            // Sync all data types
            await Promise.all([
                this.syncExpenses(userId),
                this.syncPlatforms(userId),
                this.syncReceipts(userId)
            ]);

            this.lastSyncTime = new Date();
            const result = { 
                status: SYNC_STATES.COMPLETED,
                lastSync: this.lastSyncTime
            };
            
            this.notifySubscribers(result);
            return result;
        } catch (error) {
            const errorResult = {
                status: SYNC_STATES.ERROR,
                error: handleApiError(error)
            };
            this.notifySubscribers(errorResult);
            return errorResult;
        } finally {
            this.syncInProgress = false;
        }
    }

    subscribeSyncStatus(callback) {
        this.statusSubscribers.add(callback);
        return () => this.statusSubscribers.delete(callback);
    }

    notifySubscribers(status) {
        this.statusSubscribers.forEach(callback => callback(status));
    }

    async getSyncStatus(userId) {
        try {
            const response = await apiClient.get('/sync/status', {
                params: { userId }
            });
            return response.data;
        } catch (error) {
            throw handleApiError(error);
        }
    }
}

export default new SyncService();
