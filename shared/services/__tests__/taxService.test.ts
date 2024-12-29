import { taxService } from '../taxService';
import { coreTaxService } from '../coreTaxService';
import { ApiClient } from '../apiClient';
import { CacheManager } from '../cacheManager';
import { TaxContext, FilingStatus, BusinessType } from '../../types/tax';

jest.mock('../apiClient');
jest.mock('../cacheManager');

describe('TaxService', () => {
  let mockApiClient: jest.Mocked<ApiClient>;
  let mockCacheManager: jest.Mocked<CacheManager>;

  beforeEach(() => {
    mockApiClient = new ApiClient() as jest.Mocked<ApiClient>;
    mockCacheManager = new CacheManager() as jest.Mocked<CacheManager>;
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('calculateQuarterlyTax', () => {
    it('should calculate quarterly tax correctly', async () => {
      const income = 50000;
      const expenses = 10000;
      const context: TaxContext = {
        year: 2023,
        quarter: 2,
        isAmended: false,
        filingStatus: FilingStatus.SINGLE,
        businessType: BusinessType.SOLE_PROPRIETOR
      };

      const expectedResult = {
        quarterlyAmount: 2500,
        annualEstimate: 10000,
        effectiveRate: 0.25,
        dueDate: '2023-06-15'
      };

      jest.spyOn(coreTaxService, 'calculateTax').mockResolvedValue(expectedResult);

      const result = await taxService.calculateQuarterlyTax(income, expenses);
      expect(result).toEqual(expectedResult);
    });

    it('should handle offline calculation', async () => {
      const income = 50000;
      const expenses = 10000;

      // Simulate offline
      Object.defineProperty(navigator, 'onLine', { value: false });

      const result = await taxService.calculateQuarterlyTax(income, expenses);
      expect(result.quarterlyAmount).toBeDefined();
      expect(result.annualEstimate).toBeDefined();
    });
  });

  describe('analyzeDeductions', () => {
    it('should analyze deductions correctly', async () => {
      const expenses = [
        { id: '1', amount: 1000, description: 'Office supplies' },
        { id: '2', amount: 500, description: 'Software subscription' }
      ];

      const expectedDeductions = expenses.map(expense => ({
        ...expense,
        category: 'business',
        isEligible: true,
        savings: expense.amount * 0.25
      }));

      jest.spyOn(coreTaxService, 'analyzeDeductions').mockResolvedValue(expectedDeductions);

      const result = await taxService.analyzeDeductions(expenses);
      expect(result).toEqual(expectedDeductions);
    });
  });

  describe('calculateTaxSavings', () => {
    it('should calculate tax savings correctly', async () => {
      const amount = 1000;
      const expectedSavings = 250;

      const result = await taxService.calculateTaxSavings(amount);
      expect(result).toBe(expectedSavings);
    });
  });
});
