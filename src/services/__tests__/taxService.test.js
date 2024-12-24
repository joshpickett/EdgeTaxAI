import { getTaxSavings, getDeductionSuggestions, getTaxRate, getTaxReports } from '../taxService';

describe('TaxService', () => {
  beforeEach(() => {
    global.fetch = jest.fn();
    console.error = jest.fn();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('getTaxSavings', () => {
    const mockAmount = 1000;

    it('should calculate tax savings successfully', async () => {
      const mockSavings = { savings: 250 };
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockSavings)
      });

      const result = await getTaxSavings(mockAmount);
      expect(result).toBe(mockSavings.savings);
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/tax/savings'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ amount: mockAmount })
        })
      );
    });

    it('should handle API errors', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        json: () => Promise.resolve({ error: 'Failed to calculate' })
      });

      await expect(getTaxSavings(mockAmount))
        .rejects.toThrow('Failed to fetch tax savings');
    });

    it('should handle network errors', async () => {
      global.fetch.mockRejectedValueOnce(new Error('Network error'));
      await expect(getTaxSavings(mockAmount)).rejects.toThrow();
    });

    it('should handle invalid amount input', async () => {
      await expect(getTaxSavings(-100)).rejects.toThrow();
      await expect(getTaxSavings(0)).rejects.toThrow();
      await expect(getTaxSavings('invalid')).rejects.toThrow();
    });
  });

  describe('getDeductionSuggestions', () => {
    const mockExpenses = [
      { id: 1, amount: 100, category: 'office' },
      { id: 2, amount: 200, category: 'travel' }
    ];

    it('should fetch deduction suggestions successfully', async () => {
      const mockSuggestions = [
        { category: 'office', potential: 50 },
        { category: 'travel', potential: 100 }
      ];
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ suggestions: mockSuggestions })
      });

      const result = await getDeductionSuggestions(mockExpenses);
      expect(result).toEqual(mockSuggestions);
    });

    it('should handle empty expenses array', async () => {
      const result = await getDeductionSuggestions([]);
      expect(result).toEqual([]);
    });

    it('should handle invalid expense data', async () => {
      await expect(getDeductionSuggestions(null))
        .rejects.toThrow();
      await expect(getDeductionSuggestions(undefined))
        .rejects.toThrow();
    });
  });

  describe('getTaxRate', () => {
    it('should fetch tax rate successfully', async () => {
      const mockRate = { tax_rate: 0.25 };
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockRate)
      });

      const result = await getTaxRate();
      expect(result).toBe(mockRate.tax_rate);
    });

    it('should handle API errors', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        json: () => Promise.resolve({ error: 'Rate not found' })
      });

      await expect(getTaxRate()).rejects.toThrow('Failed to fetch tax rate');
    });

    it('should handle invalid tax rate response', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ tax_rate: 'invalid' })
      });

      await expect(getTaxRate()).rejects.toThrow();
    });
  });

  describe('getTaxReports', () => {
    const mockUserId = 'user123';

    it('should fetch tax reports successfully', async () => {
      const mockReports = [
        { id: 1, year: 2023, total: 1000 },
        { id: 2, year: 2022, total: 800 }
      ];
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ reports: mockReports })
      });

      const result = await getTaxReports(mockUserId);
      expect(result).toEqual(mockReports);
    });

    it('should handle missing userId', async () => {
      await expect(getTaxReports()).rejects.toThrow();
      await expect(getTaxReports(null)).rejects.toThrow();
      await expect(getTaxReports('')).rejects.toThrow();
    });

    it('should handle unauthorized access', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: () => Promise.resolve({ error: 'Unauthorized' })
      });

      await expect(getTaxReports(mockUserId))
        .rejects.toThrow('Failed to fetch tax reports');
    });
  });
});
