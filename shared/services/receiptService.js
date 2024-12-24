import { apiClient } from './apiClient';
import config from '../config';

class ReceiptService {
    constructor() {
        this.client = apiClient;
    }

    async processReceipt(file) {
        try {
            const formData = new FormData();
            formData.append('receipt', file);

            const response = await this.client.post('/expenses/process-receipt', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });

            return response.data;
        } catch (error) {
            console.error('Receipt processing error:', error);
            throw error;
        }
    }

    async analyzeReceipt(receiptData) {
        try {
            const response = await this.client.post('/expenses/analyze-receipt', receiptData);
            return response.data;
        } catch (error) {
            console.error('Receipt analysis error:', error);
            throw error;
        }
    }
}

export default new ReceiptService();
