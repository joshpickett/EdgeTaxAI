import { apiClient } from './apiClient';
import config from '../config';
import { handleApiError } from '../utils/errorHandler';
import { TripData, MileageRecord } from '../types/interfaces';

class MileageService {
    constructor() {
        this.client = apiClient;
        this.mileageRate = config.tax.mileageRate;
        this.offlineEnabled = true;
    }

    async calculateMileage(tripData: TripData) {
        try {
            if (!navigator.onLine && this.offlineEnabled) {
                return this.calculateOfflineMileage(tripData);
            }
            const response = await this.client.post('/mileage', tripData);
            return response.data;
        } catch (error) {
            throw handleApiError(error);
        }
    }

    async addMileageRecord(record: MileageRecord) {
        try {
            const response = await this.client.post('/mileage/add', record);
            return response.data;
        } catch (error) {
            throw handleApiError(error);
        }
    }

    async getMileageHistory(userId: string) {
        try {
            const response = await this.client.get('/mileage/history', {
                params: { userId }
            });
            return response.data;
        } catch (error) {
            throw handleApiError(error);
        }
    }

    private calculateOfflineMileage(tripData: TripData) {
        return {
            distance: "Offline calculation not available",
            tax_deduction: 0
        };
    }
}

export default new MileageService();
