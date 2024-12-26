import { sharedReportingService } from '../sharedReportingService';
import { apiClient } from '../apiClient';
import { cacheManager } from '../cacheManager';
import { offlineManager } from '../offlineManager';

jest.mock('../apiClient');
jest.mock('../cacheManager');
jest.mock('../offlineManager');

describe('SharedReportingService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('generateReport', () => {
    const mockParameters = {
      startDate: '2023-01-01',
      endDate: '2023-12-31'
    };

    it('validates report parameters', async () => {
      await expect(sharedReportingService.generateReport('tax_summary', {}))
        .rejects
        .toThrow('Report parameters validation failed');
    });

    it('uses cached data when available', async () => {
      const mockCachedData = { data: 'cached' };
      cacheManager.get.mockResolvedValueOnce(mockCachedData);

      const result = await sharedReportingService.generateReport('tax_summary', mockParameters);
      expect(result).toEqual(mockCachedData);
      expect(apiClient.post).not.toHaveBeenCalled();
    });

    it('fetches and caches new data when cache miss', async () => {
      const mockResponse = { data: 'fresh' };
      cacheManager.get.mockResolvedValueOnce(null);
      apiClient.post.mockResolvedValueOnce({ data: mockResponse });

      const result = await sharedReportingService.generateReport('tax_summary', mockParameters);
      
      expect(result).toEqual(mockResponse);
      expect(cacheManager.set).toHaveBeenCalled();
    });

    it('handles offline mode', async () => {
      global.navigator.onLine = false;
      
      await sharedReportingService.generateReport('tax_summary', mockParameters);
      
      expect(offlineManager.queueOperation).toHaveBeenCalledWith({
        type: 'GENERATE_REPORT',
        data: expect.any(Object)
      });
    });
  });

  describe('fetchDashboardData', () => {
    it('fetches all required data', async () => {
      const mockData = {
        taxData: { tax: 1000 },
        incomeData: { income: 5000 },
        expenseData: { expenses: 3000 },
        planningData: { goals: [] }
      };

      jest.spyOn(sharedReportingService, 'getTaxSummary').mockResolvedValueOnce(mockData.taxData);
      jest.spyOn(sharedReportingService, 'getIncomeData').mockResolvedValueOnce(mockData.incomeData);
      jest.spyOn(sharedReportingService, 'getExpenseData').mockResolvedValueOnce(mockData.expenseData);
      jest.spyOn(sharedReportingService, 'getPlanningData').mockResolvedValueOnce(mockData.planningData);

      const result = await sharedReportingService.fetchDashboardData();
      expect(result).toEqual(mockData);
    });

    it('handles partial data fetch failures', async () => {
      jest.spyOn(sharedReportingService, 'getTaxSummary').mockRejectedValueOnce(new Error());
      
      const result = await sharedReportingService.fetchDashboardData();
      expect(result.taxData).toBeNull();
    });
  });
});
