import { setupSharedPath } from './setup_path';
setupSharedPath();

import axios from 'axios';
import config from 'config';
import { handleApiError } from 'utils/errorHandler';
import { getStoredToken, refreshToken } from 'utils/auth';

class ApiClient {
    constructor() {
        // Initialization code here
    }

    // Other methods...

    async request(config) {
        // Add platform-specific headers
        if (config.platform) {
            config.headers['X-Platform'] = config.platform;
            config.headers['X-Platform-Version'] = config.platformVersion || '1.0';
        }

        const token = getStoredToken();
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }

        try {
            const response = await this.client(config);
            // Update platform-specific tokens if needed
            if (response.data.platformTokens) {
                Object.entries(response.data.platformTokens).forEach(([platform, token]) => {
                    localStorage.setItem(`${platform}_token`, token);
                });
            }
            return response;
        } catch (error) {
            try {
                const refreshResponse = await refreshToken();
                error.config.headers.Authorization = `Bearer ${refreshResponse.data.token}`;
                return this.client(error.config);
            } catch (refreshError) {
                handleApiError(refreshError);
                throw refreshError;
            }
        }
    }

    // Other methods...
}
