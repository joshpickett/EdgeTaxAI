import IRSComplianceService from '../irsComplianceService';
import ApiClient from '../apiClient';
import { handleApiError } from '../../utils/errorHandler';

jest.mock('../apiClient');
jest.mock('../../utils/errorHandler');

describe('IRSComplianceService', () => {
    beforeEach(() => {
        jest.clearAllMocks();
    });

    describe('verifyCompliance', () => {
        const mockExpense = {
            receipt: 'receipt.jpg',
            description: 'Office supplies',
            amount: 100,
            date: '2023-01-01',
            category: 'office'
        };

        test('should verify expense compliance successfully', async () => {
            ApiClient.post.mockResolvedValueOnce({
                data: { isCompliant: true, warnings: [] }
            });

            const result = await IRSComplianceService.verifyCompliance(mockExpense);
            expect(result.isCompliant).toBe(true);
            expect(ApiClient.post).toHaveBeenCalledWith(
                '/irs/verify-compliance',
                { expense: mockExpense }
            );
        });

        test('should handle verification errors', async () => {
            const error = new Error('API Error');
            ApiClient.post.mockRejectedValueOnce(error);
            handleApiError.mockImplementationOnce(err => { throw err; });

            await expect(
                IRSComplianceService.verifyCompliance(mockExpense)
            ).rejects.toThrow('API Error');
        });
    });

    describe('generateScheduleC', () => {
        test('should generate Schedule C successfully', async () => {
            ApiClient.post.mockResolvedValueOnce({
                data: { scheduleC: 'pdf_data' }
            });

            const result = await IRSComplianceService.generateScheduleC(123, 2023);
            expect(result.scheduleC).toBe('pdf_data');
        });

        test('should handle generation errors', async () => {
            ApiClient.post.mockRejectedValueOnce(new Error('Generation failed'));
            handleApiError.mockImplementationOnce(err => { throw err; });

            await expect(
                IRSComplianceService.generateScheduleC(123, 2023)
            ).rejects.toThrow('Generation failed');
        });
    });

    describe('checkDocumentation', () => {
        test('should identify missing required fields', () => {
            const incompleteExpense = {
                description: 'Test',
                amount: 100
                // missing receipt and date
            };

            const result = IRSComplianceService.checkDocumentation(incompleteExpense);
            expect(result.isCompliant).toBe(false);
            expect(result.missingFields).toContain('receipt');
            expect(result.missingFields).toContain('date');
        });

        test('should pass complete documentation', () => {
            const completeExpense = {
                receipt: 'receipt.jpg',
                description: 'Test',
                amount: 100,
                date: '2023-01-01'
            };

            const result = IRSComplianceService.checkDocumentation(completeExpense);
            expect(result.isCompliant).toBe(true);
            expect(result.missingFields).toHaveLength(0);
        });
    });

    describe('generateSuggestions', () => {
        test('should generate appropriate suggestions for missing fields', () => {
            const missingFields = ['receipt', 'date'];
            const suggestions = IRSComplianceService.generateSuggestions(missingFields);

            expect(suggestions).toHaveLength(2);
            expect(suggestions[0].field).toBe('receipt');
            expect(suggestions[0].message).toContain('Missing required receipt');
        });
    });
});
