import {
  fetchDashboardData,
  fetchIRSReports,
  fetchExpenseData,
  fetchCustomReports
} from '../reportsService';

describe('ReportsService', () => {
  beforeEach(() => {
    global.fetch = jest.fn();
    console.error = jest.fn();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('fetchWithErrorHandling', () => {
    it('should handle successful requests', async () => {
      const mockData = { success: true };
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockData)
      });

      const result = await fetchExpenseData();
      expect(result).toEqual(mockData);
    });

    it('should handle API errors', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        json: () => Promise.resolve({ error: 'API Error' })
      });

      await expect(fetchExpenseData()).rejects.toThrow('Failed to fetch expense reports');
      expect(console.error).toHaveBeenCalled();
    });

    it('should handle network errors', async () => {
      global.fetch.mockRejectedValueOnce(new Error('Network error'));

      await expect(fetchExpenseData()).rejects.toThrow('Failed to fetch expense reports');
      expect(console.error).toHaveBeenCalled();
    });
  });

  describe('fetchDashboardData', () => {
    it('should fetch all dashboard data successfully', async () => {
      const mockData = {
        taxData: { tax: 'data' },
        incomeData: { income: 'data' },
        expenseData: { expense: 'data' },
        planningData: { planning: 'data' }
      };

      // Mock all individual fetch calls
      global.fetch.mockImplementation((url) => {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockData[url.split('/').pop()])
        });
      });

      const result = await fetchDashboardData();
      expect(result).toEqual(mockData);
    });

    it('should handle partial data fetch failures', async () => {
      global.fetch
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ tax: 'data' })
        })
        .mockRejectedValueOnce(new Error('Failed to fetch income'));

      await expect(fetchDashboardData()).rejects.toThrow('Failed to fetch income');
      expect(console.error).toHaveBeenCalled();
    });
  });

  describe('fetchIRSReports', () => {
    const mockUserId = 'user123';

    it('should fetch IRS reports successfully', async () => {
      const mockReports = { year: '2023', reports: [] };
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockReports)
      });

      const result = await fetchIRSReports(mockUserId);
      expect(result).toEqual(mockReports);
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining(`/irs/${mockUserId}`)
      );
    });

    it('should handle missing userId', async () => {
      await expect(fetchIRSReports()).rejects.toThrow();
    });

    it('should handle API errors', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        json: () => Promise.resolve({ error: 'Not found' })
      });

      await expect(fetchIRSReports(mockUserId))
        .rejects.toThrow('Failed to fetch IRS-ready reports');
    });
  });

  describe('fetchCustomReports', () => {
    const mockUserId = 'user123';
    const validFilters = {
      startDate: '2023-01-01',
      endDate: '2023-12-31',
      category: 'expenses'
    };

    it('should validate required date filters', async () => {
      const invalidFilters = { ...validFilters, startDate: null };
      await expect(fetchCustomReports(mockUserId, invalidFilters))
        .rejects.toThrow('Start date and end date are required');
    });

    it('should fetch custom reports successfully', async () => {
      const mockReports = { reports: [] };
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockReports)
      });

      const result = await fetchCustomReports(mockUserId, validFilters);
      expect(result).toEqual(mockReports);
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining(`/custom/${mockUserId}`),
        expect.objectContaining({
          method: 'POST',
          body: expect.any(String)
        })
      );
    });

    it('should handle optional category filter', async () => {
      const filtersWithoutCategory = {
        startDate: validFilters.startDate,
        endDate: validFilters.endDate
      };

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ reports: [] })
      });

      await fetchCustomReports(mockUserId, filtersWithoutCategory);
      expect(global.fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          body: expect.stringContaining('"category":""')
        })
      );
    });

    it('should handle invalid date ranges', async () => {
      const invalidDateRange = {
        startDate: '2023-12-31',
        endDate: '2023-01-01'
      };

      await expect(fetchCustomReports(mockUserId, invalidDateRange))
        .rejects.toThrow();
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty responses', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(null)
      });

      const result = await fetchExpenseData();
      expect(result).toBeNull();
    });

    it('should handle malformed JSON responses', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.reject(new Error('Invalid JSON'))
      });

      await expect(fetchExpenseData()).rejects.toThrow();
    });

    it('should handle timeout errors', async () => {
      global.fetch.mockImplementationOnce(() => 
        new Promise((_, reject) => 
          setTimeout(() => reject(new Error('Timeout')), 1000)
        )
      );

      await expect(fetchExpenseData()).rejects.toThrow();
    });
  });
});
