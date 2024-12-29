import { 
  TaxFormData, 
  TaxFormValidation, 
  TaxFormTemplate,
  TaxFormType,
  FormStatus 
} from '../types/tax-forms';
import { ApiClient } from './apiClient';
import { CacheManager } from './cacheManager';
import { OfflineQueueManager } from './offlineQueueManager';

export class TaxFormService {
  private apiClient: ApiClient;
  private cacheManager: CacheManager;
  private offlineQueue: OfflineQueueManager;
  private formTemplates: Map<TaxFormType, TaxFormTemplate>;

  constructor() {
    this.apiClient = new ApiClient();
    this.cacheManager = new CacheManager();
    this.offlineQueue = new OfflineQueueManager();
    this.formTemplates = new Map();
  }

  async loadTemplate(formType: TaxFormType): Promise<TaxFormTemplate> {
    try {
      const cached = await this.cacheManager.get(`template_${formType}`);
      if (cached) {
        return cached;
      }

      const template = await this.apiClient.get(`/api/tax/templates/${formType}`);
      await this.cacheManager.set(`template_${formType}`, template, 3600 * 24);
      this.formTemplates.set(formType, template);
      
      return template;
    } catch (error) {
      if (!navigator.onLine) {
        const offlineTemplate = this.formTemplates.get(formType);
        if (offlineTemplate) return offlineTemplate;
      }
      throw error;
    }
  }

  async validateForm(formData: TaxFormData): Promise<TaxFormValidation> {
    try {
      const template = await this.loadTemplate(formData.type);
      const validation = await this.apiClient.post('/api/tax/validate', {
        formData,
        templateId: template.id
      });
      
      return validation;
    } catch (error) {
      if (!navigator.onLine) {
        return this.performOfflineValidation(formData);
      }
      throw error;
    }
  }

  async saveForm(formData: TaxFormData): Promise<TaxFormData> {
    try {
      const validation = await this.validateForm(formData);
      if (!validation.isValid) {
        throw new Error('Form validation failed');
      }

      const savedForm = await this.apiClient.post('/api/tax/forms', formData);
      return savedForm;
    } catch (error) {
      if (!navigator.onLine) {
        await this.offlineQueue.addToQueue('saveForm', { formData });
        return {
          ...formData,
          status: FormStatus.DRAFT,
          lastModified: new Date().toISOString()
        };
      }
      throw error;
    }
  }

  async submitForm(formId: string): Promise<TaxFormData> {
    try {
      const form = await this.apiClient.post(`/api/tax/forms/${formId}/submit`);
      return form;
    } catch (error) {
      if (!navigator.onLine) {
        await this.offlineQueue.addToQueue('submitForm', { formId });
      }
      throw error;
    }
  }

  private async performOfflineValidation(formData: TaxFormData): Promise<TaxFormValidation> {
    const template = this.formTemplates.get(formData.type);
    if (!template) {
      return {
        isValid: false,
        errors: [{
          field: 'general',
          message: 'Cannot validate form offline without template',
          code: 'TEMPLATE_MISSING'
        }],
        warnings: []
      };
    }

    const errors = [];
    const warnings = [];

    // Perform basic offline validation
    for (const field of template.fields) {
      if (field.required && !formData.data[field.name]) {
        errors.push({
          field: field.name,
          message: `${field.name} is required`,
          code: 'REQUIRED'
        });
      }
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings
    };
  }
}

export const taxFormService = new TaxFormService();
