import { 
  fetchDashboardData, 
  fetchIRSReports, 
  fetchExpenseData, 
  fetchCustomReports,
  validateReportData 
} from '../reportsService';

describe('ReportsService', () => {
  beforeEach(() => {
    fetch.mockClear();
    global.fetch = jest.fn();
  });

  describe('fetchDashboardData', () => {
    it('successfully fetches all dashboard data', async () => {
      const mockData = {
        taxData: { tax: 1000 },
        incomeData: { income: 5000 },
        expenseData: { expenses: 3000 },
        planningData: { goals: [] }
      };

      fetch.mockImplementation(() => 
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockData)
        })
      );

      const result = await fetchDashboardData();
      expect(result).toEqual(mockData);
    });

    it('handles API errors', async () => {
      fetch.mockImplementation(() => 
        Promise.resolve({
          ok: false,
          json: () => Promise.resolve({ error: 'API Error' })
        })
      );

      await expect(fetchDashboardData()).rejects.toThrow();
    });
  });

  describe('fetchIRSReports', () => {
    it('successfully fetches IRS reports', async () => {
      const mockReports = { reports: [] };
      fetch.mockImplementation(() => 
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockReports)
        })
      );

      const result = await fetchIRSReports('user123');
      expect(result).toEqual(mockReports);
    });
  });

  describe('fetchExpenseData', () => {
    it('successfully fetches expense data', async () => {
      const mockExpenses = { expenses: [] };
      fetch.mockImplementation(() => 
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockExpenses)
        })
      );

      const result = await fetchExpenseData();
      expect(result).toEqual(mockExpenses);
    });
  });

  describe('fetchCustomReports', () => {
    it('validates date inputs', async () => {
      await expect(fetchCustomReports('user123', {}))
        .rejects
        .toThrow('Start date and end date are required.');
    });

    it('successfully fetches custom reports', async () => {
      const mockReports = { reports: [] };
      fetch.mockImplementation(() => 
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockReports)
        })
      );

      const result = await fetchCustomReports('user123', {
        startDate: '2023-01-01',
        endDate: '2023-12-31'
      });
      expect(result).toEqual(mockReports);
    });
  });

  describe('validateReportData', () => {
    it('validates report data correctly', () => {
      const validData = {
        startDate: '2023-01-01',
        endDate: '2023-12-31'
      };
      const result = validateReportData(validData);
      expect(result.isValid).toBe(true);
    });

    it('handles invalid date ranges', () => {
      const invalidData = {
        startDate: '2023-12-31',
        endDate: '2023-01-01'
      };
      const result = validateReportData(invalidData);
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('End date must be after start date');
    });
  });
});
