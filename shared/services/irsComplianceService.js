import config from '../config';
import { handleApiError } from '../utils/errorHandler';
import ApiClient from './apiClient';

class IRSComplianceService {
    constructor() {
        this.client = ApiClient;
        this.complianceRules = {
            documentation: {
                required: ['receipt', 'description', 'amount', 'date'],
                optional: ['category', 'notes']
            },
            categories: {
                business: ['office', 'travel', 'meals'],
                personal: ['medical', 'charity', 'education']
            }
        };
    }

    async verifyCompliance(expense) {
        try {
            const response = await this.client.post('/irs/verify-compliance', {
                expense
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

    checkDocumentation(expense) {
        const missingFields = this.complianceRules.documentation.required.filter(
            field => !expense[field]
        );
        
        return {
            isCompliant: missingFields.length === 0,
            missingFields,
            suggestions: this.generateSuggestions(missingFields)
        };
    }

    generateSuggestions(missingFields) {
        return missingFields.map(field => ({
            field,
            message: `Missing required ${field} documentation for IRS compliance`
        }));
    }
}

export default new IRSComplianceService();
