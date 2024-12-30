import { ApiClient } from './apiClient';
import { CacheManager } from './cacheManager';
import { IRSFormData, IRSSubmissionResult, IRSValidationRule } from '../types/irs';

export class IRSComplianceService {
  private apiClient: ApiClient;
  private cacheManager: CacheManager;

  constructor() {
    this.apiClient = new ApiClient();
    this.cacheManager = new CacheManager();
  }

  async validateForm(formData: IRSFormData): Promise<{
    isValid: boolean;
    errors: Array<{ field: string; message: string }>;
  }> {
    try {
      const response = await this.apiClient.post('/api/irs/validate', formData);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async submitForm(formData: IRSFormData): Promise<IRSSubmissionResult> {
    try {
      const validation = await this.validateForm(formData);
      if (!validation.isValid) {
        throw new Error('Form validation failed');
      }

      const response = await this.apiClient.post('/api/irs/submit', formData);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async checkSubmissionStatus(submissionId: string): Promise<IRSSubmissionResult> {
    try {
      const response = await this.apiClient.get(`/api/irs/status/${submissionId}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getValidationRules(formType: string): Promise<IRSValidationRule[]> {
    try {
      const cached = await this.cacheManager.get(`irs_rules_${formType}`);
      if (cached) {
        return cached;
      }

      const response = await this.apiClient.get(`/api/irs/rules/${formType}`);
      await this.cacheManager.set(`irs_rules_${formType}`, response.data, 3600);
      return response.data;
    } catch (error) {
      throw error;
    }
  }
}

export const irsComplianceService = new IRSComplianceService();
