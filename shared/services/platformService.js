import config from '../config';
import { handleApiError } from '../utils/errorHandler';
import ApiClient from './apiClient';

class PlatformService {
    constructor() {
        this.client = ApiClient;
        this.platforms = config.platforms;
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
}

export default new PlatformService();
