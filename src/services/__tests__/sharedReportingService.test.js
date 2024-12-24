import { sharedReportingService } from '../sharedReportingService';
import { apiClient } from '../apiClient';
import { offlineManager } from '../offlineManager';

// Mock dependencies
jest.mock('../apiClient');
jest.mock('../offlineManager');

describe('SharedReportingService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Reset navigator.onLine
    Object.defineProperty(global.navigator, 'onLine', {
      writable: true,
      value: true
    });
  });

  describe('generateReport', () => {
    it('should generate report successfully', async () => {
      const mockReport = { data: 'test report' };
      apiClient.post.mockResolvedValueOnce({ data: mockReport });

      const result = await sharedReportingService.generateReport('tax_summary');
      expect(result).toEqual(mockReport);
      expect(apiClient.post).toHaveBeenCalledWith('/reports/tax_summary', {});
    });

    it('should queue report generation when offline', async () => {
      Object.defineProperty(global.navigator, 'onLine', { value: false });
      apiClient.post.mockRejectedValueOnce(new Error('Network error'));

      const result = await sharedReportingService.generateReport('tax_summary');
      
      expect(result).toBeNull();
      expect(offlineManager.queueOperation).toHaveBeenCalledWith({
        type: 'GENERATE_REPORT',
        data: { reportType: 'tax_summary', params: {} }
      });
    });

    it('should handle API errors', async () => {
      apiClient.post.mockRejectedValueOnce(new Error('API error'));

      await expect(sharedReportingService.generateReport('tax_summary'))
        .rejects.toThrow('API error');
    });
  });

  describe('fetchDashboardData', () => {
    it('should fetch all dashboard data successfully', async () => {
      const mockData = {
        taxData: { tax: 'summary' },
        incomeData: { income: 'data' },
        expenseData: { expense: 'data' },
        planningData: { planning: 'data' }
      };

      // Mock individual data fetches
      jest.spyOn(sharedReportingService, 'getTaxSummary')
        .mockResolvedValueOnce(mockData.taxData);
      jest.spyOn(sharedReportingService, 'getIncomeData')
        .mockResolvedValueOnce(mockData.incomeData);
      jest.spyOn(sharedReportingService, 'getExpenseData')
        .mockResolvedValueOnce(mockData.expenseData);
      jest.spyOn(sharedReportingService, 'getPlanningData')
        .mockResolvedValueOnce(mockData.planningData);

      const result = await sharedReportingService.fetchDashboardData();
      expect(result).toEqual(mockData);
    });

    it('should handle partial data fetch failures', async () => {
      jest.spyOn(sharedReportingService, 'getTaxSummary')
        .mockRejectedValueOnce(new Error('Failed to fetch tax data'));

      await expect(sharedReportingService.fetchDashboardData())
        .rejects.toThrow('Failed to fetch tax data');
    });
  });

  describe('exportReport', () => {
    it('should export report successfully', async () => {
      const mockExport = { url: 'export-url' };
      apiClient.post.mockResolvedValueOnce({ data: mockExport });

      const result = await sharedReportingService.exportReport('tax_summary', 'pdf');
      
      expect(result).toEqual(mockExport);
      expect(apiClient.post).toHaveBeenCalledWith(
        '/reports/export/tax_summary',
        { format: 'pdf' }
      );
    });

    it('should handle export errors', async () => {
      apiClient.post.mockRejectedValueOnce(new Error('Export failed'));

      await expect(sharedReportingService.exportReport('tax_summary', 'pdf'))
        .rejects.toThrow('Export failed');
    });

    it('should handle invalid export formats', async () => {
      await expect(sharedReportingService.exportReport('tax_summary', 'invalid'))
        .rejects.toThrow();
    });
  });

  describe('Report Types', () => {
    it('should have all required report types', () => {
      expect(sharedReportingService.reportTypes).toEqual({
        TAX_SUMMARY: 'tax_summary',
        QUARTERLY: 'quarterly',
        EXPENSE: 'expense',
        INCOME: 'income',
        CUSTOM: 'custom'
      });
    });

    it('should generate reports for all types', async () => {
      const mockResponse = { data: 'test' };
      apiClient.post.mockResolvedValue({ data: mockResponse });

      for (const type of Object.values(sharedReportingService.reportTypes)) {
        const result = await sharedReportingService.generateReport(type);
        expect(result).toEqual(mockResponse);
      }
    });
  });
});
