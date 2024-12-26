import { getTaxSavings, analyzeDeductions, getTaxRate, getTaxReports } from '../taxService';
import sharedTaxService from '../../../shared/services/taxService';

jest.mock('../../../shared/services/taxService');

describe('taxService', () => {
  beforeEach(() => {
    fetch.mockClear();
    sharedTaxService.calculateTaxSavings.mockClear();
    sharedTaxService.analyzeTaxDeductions.mockClear();
  });

  describe('getTaxSavings', () => {
    it('calculates tax savings successfully', async () => {
      const mockAmount = 1000;
      const mockSavings = 250;
      
      sharedTaxService.calculateTaxSavings.mockResolvedValueOnce(mockSavings);
      
      const result = await getTaxSavings(mockAmount);
      expect(result).toBe(mockSavings);
      expect(sharedTaxService.calculateTaxSavings).toHaveBeenCalledWith(mockAmount);
    });

    it('handles errors in tax savings calculation', async () => {
      sharedTaxService.calculateTaxSavings.mockRejectedValueOnce(new Error('Calculation failed'));
      
      await expect(getTaxSavings(1000)).rejects.toThrow('Calculation failed');
    });
  });

  describe('analyzeDeductions', () => {
    const mockExpenses = [
      { amount: 100, category: 'office' }
    ];

    it('analyzes deductions successfully', async () => {
      const mockAnalysis = { 
        totalDeductions: 100,
        categories: { office: 100 }
      };
      
      sharedTaxService.analyzeTaxDeductions.mockResolvedValueOnce(mockAnalysis);
      
      const result = await analyzeDeductions(mockExpenses);
      expect(result).toEqual(mockAnalysis);
    });

    it('handles errors in deduction analysis', async () => {
      sharedTaxService.analyzeTaxDeductions.mockRejectedValueOnce(new Error('Analysis failed'));
      
      await expect(analyzeDeductions(mockExpenses)).rejects.toThrow('Analysis failed');
    });
  });

  describe('getTaxRate', () => {
    it('fetches tax rate successfully', async () => {
      const mockResponse = { tax_rate: 0.25 };
      fetch.mockResponseOnce(JSON.stringify(mockResponse));

      const result = await getTaxRate();
      expect(result).toBe(0.25);
    });

    it('handles errors in tax rate fetch', async () => {
      fetch.mockResponseOnce(JSON.stringify({ error: 'Failed' }), { status: 400 });
      
      await expect(getTaxRate()).rejects.toThrow('Failed to fetch tax rate');
    });
  });

  describe('getTaxReports', () => {
    it('fetches tax reports successfully', async () => {
      const mockReports = [{ id: 1, year: 2023 }];
      fetch.mockResponseOnce(JSON.stringify({ reports: mockReports }));

      const result = await getTaxReports('user123');
      expect(result).toEqual(mockReports);
    });

    it('handles errors in tax reports fetch', async () => {
      fetch.mockResponseOnce(JSON.stringify({ error: 'Failed' }), { status: 400 });
      
      await expect(getTaxReports('user123')).rejects.toThrow('Failed to fetch tax reports');
    });
  });
});
