import TaxService from '../taxService';
import ApiClient from '../apiClient';
import { handleApiError } from '../../utils/errorHandler';
import { OfflineQueueManager } from '../offlineQueueManager';

jest.mock('../apiClient');
jest.mock('../offlineQueueManager');
jest.mock('../../utils/errorHandler');

describe('TaxService', () => {
    let taxService;

    beforeEach(() => {
        taxService = new TaxService();
        jest.clearAllMocks();
        global.navigator.onLine = true;
    });

    describe('calculateQuarterlyTax', () => {
        const mockParameters = {
            quarter: 1,
            year: 2023,
            income: 10000
        };

        test('should calculate tax online', async () => {
            ApiClient.post.mockResolvedValueOnce({
                data: { estimatedTax: 2500 }
            });

            const result = await taxService.calculateQuarterlyTax(mockParameters);
            expect(result.estimatedTax).toBe(2500);
        });

        test('should queue calculation when offline', async () => {
            global.navigator.onLine = false;
            await taxService.calculateQuarterlyTax(mockParameters);
            expect(taxService.offlineQueue.push).toHaveBeenCalled();
        });
    });

    describe('getTaxDeductions', () => {
        const mockExpenses = [
            { description: 'Office supplies', amount: 100 }
        ];

        test('should fetch deductions successfully', async () => {
            ApiClient.post.mockResolvedValueOnce({
                data: { totalDeductions: 100 }
            });

            const result = await taxService.getTaxDeductions(mockExpenses);
            expect(result.totalDeductions).toBe(100);
        });
    });

    describe('analyzeTaxContext', () => {
        test('should analyze tax context successfully', async () => {
            ApiClient.post.mockResolvedValueOnce({
                data: { category: 'business', deductible: true }
            });

            const result = await taxService.analyzeTaxContext(
                'Office rent',
                1000
            );
            expect(result.data.category).toBe('business');
        });
    });

    describe('verifyInternalRevenueServiceCompliance', () => {
        const mockExpense = {
            description: 'Business lunch',
            amount: 50,
            date: '2023-01-01'
        };

        test('should verify compliance successfully', async () => {
            ApiClient.post.mockResolvedValueOnce({
                data: { isCompliant: true }
            });

            const result = await taxService.verifyInternalRevenueServiceCompliance(mockExpense);
            expect(result.isCompliant).toBe(true);
        });

        test('should handle compliance verification errors', async () => {
            ApiClient.post.mockRejectedValueOnce(new Error('Verification failed'));
            handleApiError.mockImplementationOnce(err => { throw err; });

            await expect(
                taxService.verifyInternalRevenueServiceCompliance(mockExpense)
            ).rejects.toThrow('Verification failed');
        });
    });
});
