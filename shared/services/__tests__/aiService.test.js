import AIService from '../aiService';
import { apiClient } from '../apiClient';
import config from '../../config';

jest.mock('../apiClient');

describe('AIService', () => {
    let aiService;

    beforeEach(() => {
        aiService = new AIService();
        jest.clearAllMocks();
    });

    describe('categorizeExpense', () => {
        const mockExpense = {
            description: 'Uber ride to airport',
            amount: 50,
            date: '2023-01-01'
        };

        test('should use online categorization when online', async () => {
            global.navigator.onLine = true;
            apiClient.post.mockResolvedValueOnce({
                data: { category: 'transport', confidence: 0.9 }
            });

            const result = await aiService.categorizeExpense(mockExpense);
            expect(result.category).toBe('transport');
            expect(result.confidence).toBe(0.9);
        });

        test('should fallback to offline categorization when offline', async () => {
            global.navigator.onLine = false;
            const result = await aiService.categorizeExpense(mockExpense);
            
            expect(result.category).toBe('transport');
            expect(result.method).toBe('offline');
        });

        test('should handle API errors gracefully', async () => {
            global.navigator.onLine = true;
            apiClient.post.mockRejectedValueOnce(new Error('API Error'));

            const result = await aiService.categorizeExpense(mockExpense);
            expect(result.method).toBe('offline');
        });
    });

    describe('analyzeReceipt', () => {
        test('should analyze receipt text successfully', async () => {
            const mockReceiptText = 'Office supplies - $50.00';
            apiClient.post.mockResolvedValueOnce({
                data: {
                    category: 'supplies',
                    amount: 50.00,
                    confidence: 0.95
                }
            });

            const result = await aiService.analyzeReceipt(mockReceiptText);
            expect(result.category).toBe('supplies');
            expect(result.amount).toBe(50.00);
        });

        test('should handle receipt analysis errors', async () => {
            const mockReceiptText = 'Invalid receipt';
            apiClient.post.mockRejectedValueOnce(new Error('Analysis failed'));

            await expect(aiService.analyzeReceipt(mockReceiptText))
                .rejects.toThrow('Analysis failed');
        });
    });
});
