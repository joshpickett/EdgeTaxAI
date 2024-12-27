import { handleApiError } from '@desktop/utils/errorHandler';
import sharedTaxService from '@shared/services/taxService';

class AIServiceAdapter {
    async categorizeExpense(description, amount) {
        try {
            return await sharedTaxService.getOptimizationSuggestions({ description, amount });
        } catch (error) {
            throw handleApiError(error);
        }
    }

    async analyzeTaxContext(description, amount) {
        try {
            return await sharedTaxService.analyzeTaxContext(description, amount);
        } catch (error) {
            throw handleApiError(error);
        }
    }

    // ...rest of the code...
}
