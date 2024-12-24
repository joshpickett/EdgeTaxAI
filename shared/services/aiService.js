import { apiClient } from './apiClient';
import config from '../config';

class AIService {
    constructor() {
        this.categories = {
            transport: ['uber', 'lyft', 'taxi', 'gas', 'parking'],
            meals: ['restaurant', 'food', 'cafe'],
            supplies: ['office', 'supplies', 'equipment'],
            utilities: ['phone', 'internet', 'electricity']
        };
        this.confidenceThreshold = 0.7;
    }

    async categorizeExpense(expense) {
        try {
            if (navigator.onLine) {
                return await this.onlineCategorization(expense);
            }
            return this.offlineCategorization(expense);
        } catch (error) {
            console.error('Categorization error:', error);
            return this.offlineCategorization(expense);
        }
    }

    async onlineCategorization(expense) {
        try {
            const response = await apiClient.post('/ai/categorize', {
                description: expense.description,
                amount: expense.amount,
                date: expense.date
            });
            return response.data;
        } catch (error) {
            console.error('Online categorization error:', error);
            throw error;
        }
    }

    offlineCategorization(expense) {
        const description = expense.description.toLowerCase();
        
        for (const [category, keywords] of Object.entries(this.categories)) {
            if (keywords.some(keyword => description.includes(keyword))) {
                return {
                    category,
                    confidence: 0.8,
                    method: 'offline'
                };
            }
        }

        return {
            category: 'other',
            confidence: 0.5,
            method: 'offline'
        };
    }

    async analyzeReceipt(receiptText) {
        try {
            const response = await apiClient.post('/ai/analyze-receipt', {
                text: receiptText
            });
            return response.data;
        } catch (error) {
            console.error('Receipt analysis error:', error);
            throw error;
        }
    }
}

export default new AIService();
