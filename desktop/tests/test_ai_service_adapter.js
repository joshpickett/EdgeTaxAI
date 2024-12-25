import { jest } from '@jest/globals';
import AIServiceAdapter from '../services/ai_service_adapter';
import sharedTaxService from '../../shared/services/taxService';

describe('AIServiceAdapter', () => {
    let aiService;
    
    beforeEach(() => {
        aiService = new AIServiceAdapter();
        jest.clearAllMocks();
    });

    describe('categorizeExpense', () => {
        it('should successfully categorize expense', async () => {
            const mockExpense = {
                description: 'Uber ride',
                amount: 25.00
            };
            
            const mockResponse = {
                category: 'transportation',
                confidence: 0.95
            };
            
            jest.spyOn(sharedTaxService, 'getOptimizationSuggestions')
                .mockResolvedValue(mockResponse);
                
            const result = await aiService.categorizeExpense(
                mockExpense.description, 
                mockExpense.amount
            );
            
            expect(result).toEqual(mockResponse);
            expect(sharedTaxService.getOptimizationSuggestions)
                .toHaveBeenCalledWith(mockExpense);
        });

        it('should handle errors gracefully', async () => {
            const mockError = new Error('API Error');
            jest.spyOn(sharedTaxService, 'getOptimizationSuggestions')
                .mockRejectedValue(mockError);
                
            await expect(aiService.categorizeExpense('test', 100))
                .rejects.toThrow('API Error');
        });
    });

    describe('analyzeTaxContext', () => {
        it('should analyze tax context successfully', async () => {
            const mockData = {
                description: 'Office supplies',
                amount: 50.00
            };
            
            const mockResponse = {
                deductible: true,
                category: 'business_supplies',
                confidence: 0.9
            };
            
            jest.spyOn(sharedTaxService, 'analyzeTaxContext')
                .mockResolvedValue(mockResponse);
                
            const result = await aiService.analyzeTaxContext(
                mockData.description,
                mockData.amount
            );
            
            expect(result).toEqual(mockResponse);
            expect(sharedTaxService.analyzeTaxContext)
                .toHaveBeenCalledWith(mockData.description, mockData.amount);
        });

        it('should handle analysis errors', async () => {
            const mockError = new Error('Analysis failed');
            jest.spyOn(sharedTaxService, 'analyzeTaxContext')
                .mockRejectedValue(mockError);
                
            await expect(aiService.analyzeTaxContext('test', 100))
                .rejects.toThrow('Analysis failed');
        });
    });
});
