import { setupSharedPath } from './setup_path';
setupSharedPath();

import { apiClient } from './apiClient';
import { handleApiError } from 'utils/errorHandler';
import { PLATFORMS } from 'constants';

class PlatformConnectionService {
    constructor() {
        this.connections = new Map();
    }

    async connectPlatform(platform, userId) {
        try {
            const response = await apiClient.post(`/platforms/${platform}/connect`, {
                userId
            });
            
            this.connections.set(platform, {
                userId,
                connected: true,
                lastSync: new Date()
            });
            
            return response.data;
        } catch (error) {
            throw handleApiError(error);
        }
    }

    async disconnectPlatform(platform, userId) {
        try {
            const response = await apiClient.post(`/platforms/${platform}/disconnect`, {
                userId
            });
            
            this.connections.delete(platform);
            return response.data;
        } catch (error) {
            throw handleApiError(error);
        }
    }

    async getConnectedPlatforms(userId) {
        try {
            const response = await apiClient.get('/platforms/connected', {
                params: { userId }
            });
            return response.data;
        } catch (error) {
            throw handleApiError(error);
        }
    }

    async validateConnection(platform, userId) {
        try {
            const response = await apiClient.get(`/platforms/${platform}/validate`, {
                params: { userId }
            });
            return response.data;
        } catch (error) {
            throw handleApiError(error);
        }
    }
}

export default new PlatformConnectionService();
