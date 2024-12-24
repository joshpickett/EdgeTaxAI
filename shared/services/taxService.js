import config from '../config';
import { handleApiError } from '../utils/errorHandler';
import ApiClient from './apiClient';
import { TaxCalculation, QuarterlyEstimate, IRSCompliance } from '../types/tax';
import { OfflineQueueManager } from './offlineQueueManager';

class TaxService {
    constructor() {
        this.client = ApiClient;
        this.taxRates = {
            ...config.tax,
            deductionCategories: {
                business: ['office', 'travel', 'meals'],
                personal: ['medical', 'charity', 'education']
            }
        };
        this.lastCalculation = null;
        this.offlineQueue = new OfflineQueueManager();
    }

    async calculateWithOfflineSupport(operation, params) {
        try {
            if (!navigator.onLine) {
                this.offlineQueue.push({ operation, params });
                return this.getOfflineEstimate(operation, params);
            }
            return await operation(params);
        } catch (error) {
            throw handleApiError(error);
        }
    }

    async calculateQuarterlyTax(params: QuarterlyEstimate): Promise<TaxCalculation> {
        return this.offlineQueue.processWithOfflineSupport(
            'calculateTax',
            params
        );
    }

    async getTaxDeductions(expenses) {
        try {
            const response = await this.client.post('/tax/deductions', {
                expenses
            });
            return response.data;
        } catch (error) {
            throw handleApiError(error);
        }
    }

    async getOptimizationSuggestions(data) {
        try {
            const response = await this.client.post('/tax-optimization/optimize', {
                data
            });
            return response.data;
        } catch (error) {
            throw handleApiError(error);
        }
    }

    async generateScheduleC(userId, year) {
        try {
            const response = await this.client.post('/irs/generate-schedule-c', {
                userId,
                year
            });
            return response.data;
        } catch (error) {
            throw handleApiError(error);
        }
    }

    async analyzeTaxContext(description, amount) {
        try {
            return await this.client.post('/tax/analyze-context', {
                description,
                amount
            });
        } catch (error) {
            throw handleApiError(error);
        }
    }

    async analyzeTaxDeductions(expenses) {
        try {
            const categorizedExpenses = expenses.map(expense => ({
                ...expense,
                category: this.categorizeExpense(expense.description)
            }));
            
            return {
                deductions: categorizedExpenses,
                totalDeductible: this.calculateTotalDeductions(categorizedExpenses)
            };
        } catch (error) {
            throw handleApiError(error);
        }
    }

    calculateTaxSavings(amount) {
        return amount * this.taxRates.selfEmploymentTaxRate;
    }

    async verifyIRSCompliance(expense) {
        try {
            const response = await this.client.post('/irs/verify-compliance', {
                expense
            });
            return response.data;
        } catch (error) {
            throw handleApiError(error);
        }
    }
}

export default new TaxService();
