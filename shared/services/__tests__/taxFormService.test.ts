import { taxFormService } from '../taxFormService';
import { ApiClient } from '../apiClient';
import { CacheManager } from '../cacheManager';
import { 
  TaxFormType, 
  FormStatus, 
  TaxFormData,
  TaxFormTemplate 
} from '../../types/tax-forms';

jest.mock('../apiClient');
jest.mock('../cacheManager');

describe('TaxFormService', () => {
  let mockApiClient: jest.Mocked<ApiClient>;
  let mockCacheManager: jest.Mocked<CacheManager>;

  const mockTemplate: TaxFormTemplate = {
    id: 'template_1040_2023',
    type: TaxFormType.FORM_1040,
    fields: [
      {
        id: 'income',
        name: 'totalIncome',
        type: 'number',
        required: true
      },
      {
        id: 'deductions',
        name: 'totalDeductions',
        type: 'number',
        required: true
      }
    ],
    validations: [],
    calculations: []
  };

  const mockFormData: TaxFormData = {
    id: '123',
    type: TaxFormType.FORM_1040,
    year: 2023,
    status: FormStatus.DRAFT,
    data: {
      totalIncome: 50000,
      totalDeductions: 10000
    }
  };

  beforeEach(() => {
    mockApiClient = new ApiClient() as jest.Mocked<ApiClient>;
    mockCacheManager = new CacheManager() as jest.Mocked<CacheManager>;
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('loadTemplate', () => {
    it('should load template from cache if available', async () => {
      mockCacheManager.get.mockResolvedValue(mockTemplate);

      const result = await taxFormService.loadTemplate(TaxFormType.FORM_1040);
      expect(result).toEqual(mockTemplate);
      expect(mockCacheManager.get).toHaveBeenCalledWith('template_1040');
    });

    it('should fetch template from API if not in cache', async () => {
      mockCacheManager.get.mockResolvedValue(null);
      mockApiClient.get.mockResolvedValue(mockTemplate);

      const result = await taxFormService.loadTemplate(TaxFormType.FORM_1040);
      expect(result).toEqual(mockTemplate);
      expect(mockApiClient.get).toHaveBeenCalled();
    });
  });

  describe('validateForm', () => {
    it('should validate form successfully', async () => {
      const mockValidation = {
        isValid: true,
        errors: [],
        warnings: []
      };

      mockApiClient.post.mockResolvedValue(mockValidation);

      const result = await taxFormService.validateForm(mockFormData);
      expect(result).toEqual(mockValidation);
    });

    it('should perform offline validation when offline', async () => {
      Object.defineProperty(navigator, 'onLine', { value: false });

      const result = await taxFormService.validateForm(mockFormData);
      expect(result.isValid).toBeDefined();
    });
  });

  describe('saveForm', () => {
    it('should save form successfully', async () => {
      const mockValidation = {
        isValid: true,
        errors: [],
        warnings: []
      };

      mockApiClient.post.mockResolvedValueOnce(mockValidation);
      mockApiClient.post.mockResolvedValueOnce(mockFormData);

      const result = await taxFormService.saveForm(mockFormData);
      expect(result).toEqual(mockFormData);
    });

    it('should queue form for offline saving when offline', async () => {
      Object.defineProperty(navigator, 'onLine', { value: false });

      const result = await taxFormService.saveForm(mockFormData);
      expect(result.status).toBe(FormStatus.DRAFT);
    });
  });

  describe('submitForm', () => {
    it('should submit form successfully', async () => {
      const submittedForm = {
        ...mockFormData,
        status: FormStatus.SUBMITTED
      };

      mockApiClient.post.mockResolvedValue(submittedForm);

      const result = await taxFormService.submitForm(mockFormData.id);
      expect(result.status).toBe(FormStatus.SUBMITTED);
    });
  });
});
