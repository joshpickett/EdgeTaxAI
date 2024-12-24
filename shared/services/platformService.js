import config from '../config';
import { handleApiError } from '../utils/errorHandler';
import ApiClient from './apiClient';
import { PLATFORMS } from '../constants';

class PlatformService {
    constructor() {
        this.client = ApiClient;
        this.platforms = config.platforms;
        this.syncInProgress = false;
        this.lastSyncTime = null;
    }

    async connectPlatform(platform, userId) {
        try {
            const response = await this.client.post(`/platforms/connect/${platform}`, {
                userId,
                platform
            });
            return response.data;
        } catch (error) {
            throw handleApiError(error);
        }
    }

    async disconnectPlatform(platform, userId) {
        try {
            const response = await this.client.post(`/platforms/disconnect/${platform}`, {
                userId,
                platform
            });
            return response.data;
        } catch (error) {
            throw handleApiError(error);
        }
    }

    async syncPlatformData(platform, userId) {
        try {
            const response = await this.client.post(`/platforms/sync/${platform}`, {
                userId,
                platform
            });
            return response.data;
        } catch (error) {
            throw handleApiError(error);
        }
    }

    async getPlatformStatus(platform, userId) {
        try {
            const response = await this.client.get(`/platforms/status/${platform}`, {
                params: { userId }
            });
            return response.data;
        } catch (error) {
            throw handleApiError(error);
        }
    }

    async syncAllPlatforms(userId) {
        if (this.syncInProgress) return;
        
        try {
            this.syncInProgress = true;
            const platforms = Object.values(PLATFORMS);
            
            for (const platform of platforms) {
                await this.syncPlatformData(platform, userId);
            }
            
            this.lastSyncTime = new Date();
            return true;
        } catch (error) {
            throw handleApiError(error);
        } finally {
            this.syncInProgress = false;
        }
    }
}

export default new PlatformService();
