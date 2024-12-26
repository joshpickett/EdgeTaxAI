import ReportsService from '../reportsService';
import { apiClient } from '../apiClient';
import { cacheManager } from '../cacheManager';
import { validateReportData } from '../../utils/validation';

jest.mock('../apiClient');
jest.mock('../cacheManager');
jest.mock('../../utils/validation');

describe('ReportsService', () => {
    let reportsService;

    beforeEach(() => {
        reportsService = new ReportsService();
        jest.clearAllMocks();
    });

    describe('generateReport', () => {
        const mockParameters = {
            startDate: '2023-01-01',
            endDate: '2023-12-31',
            type: 'quarterly'
        };

        test('should generate report successfully', async () => {
            validateReportData.mockReturnValue({ isValid: true });
            apiClient.post.mockResolvedValueOnce({
                data: { report: 'test_data' }
            });

            const result = await reportsService.generateReport('tax_summary', mockParameters);
            expect(result).toEqual({ report: 'test_data' });
        });

        test('should return cached report if available', async () => {
            const cachedData = { report: 'cached_data' };
            cacheManager.get.mockResolvedValueOnce(cachedData);

            const result = await reportsService.generateReport('tax_summary', mockParameters);
            expect(result).toEqual(cachedData);
            expect(apiClient.post).not.toHaveBeenCalled();
        });

        test('should handle validation errors', async () => {
            validateReportData.mockReturnValue({
                isValid: false,
                errors: ['Invalid date range']
            });

            await expect(
                reportsService.generateReport('tax_summary', mockParameters)
            ).rejects.toThrow('Invalid date range');
        });
    });
});
