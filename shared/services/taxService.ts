import { TaxCalculationResult, TaxDeduction, TaxForm } from '../types/tax';
import { IRSFormData, IRSSubmissionResult } from '../types/irs';
import { ApiClient } from './apiClient';
import { OfflineQueueManager } from './offlineQueueManager';
import { coreTaxService } from './coreTaxService';
import { irsComplianceService } from './irsComplianceService';

export class TaxService {
  private apiClient: ApiClient;
  private offlineQueue: OfflineQueueManager;
  private coreTaxService: typeof coreTaxService;

  constructor() {
    this.apiClient = new ApiClient();
    this.offlineQueue = new OfflineQueueManager();
    this.coreTaxService = coreTaxService;
  }

  async calculateQuarterlyTax(income: number, expenses: number): Promise<TaxCalculationResult> {
    try {
      const context = { year: new Date().getFullYear(), quarter: this.getCurrentQuarter() };
      const result = await this.coreTaxService.calculateTax(income, expenses, context);
 
      return result;
    } catch (error) {
      if (!navigator.onLine) {
        await this.offlineQueue.addToQueue('calculateQuarterlyTax', { income, expenses });
      }
      throw error;
    }
  }

  async analyzeDeductions(expenses: any[]): Promise<TaxDeduction[]> {
    try {
      const result = await this.apiClient.post('/api/tax/deductions', { expenses });
      return result.deductions;
    } catch (error) {
      if (!navigator.onLine) {
        await this.offlineQueue.addToQueue('analyzeDeductions', { expenses });
      }
      throw error;
    }
  }

  async generateTaxForm(formType: string, data: any): Promise<TaxForm> {
    try {
      const result = await this.apiClient.post(`/api/tax/forms/${formType}`, data);
      return result.form;
    } catch (error) {
      if (!navigator.onLine) {
        await this.offlineQueue.addToQueue('generateTaxForm', { formType, data });
      }
      throw error;
    }
  }

  async calculateTaxSavings(amount: number): Promise<number> {
    try {
      const result = await this.apiClient.post('/api/tax/savings', { amount });
      return result.savings;
    } catch (error) {
      if (!navigator.onLine) {
        return this.estimateTaxSavings(amount);
      }
      throw error;
    }
  }

  private estimateTaxSavings(amount: number): number {
    // Fallback calculation when offline
    return amount * 0.25; // Simple 25% estimate
  }

  private getCurrentQuarter(): number {
    const month = new Date().getMonth() + 1; // Months are 0-indexed
    return Math.ceil(month / 3);
  }

  async submitToIRS(formData: IRSFormData): Promise<IRSSubmissionResult> {
    try {
      return await irsComplianceService.submitForm(formData);
    } catch (error) {
      if (!navigator.onLine) {
        await this.offlineQueue.addToQueue('submitToIRS', { formData });
      }
      throw error;
    }
  }

  async checkIRSSubmissionStatus(submissionId: string): Promise<IRSSubmissionResult> {
    try {
      return await irsComplianceService.checkSubmissionStatus(submissionId);
    } catch (error) {
      throw error;
    }
  }
}

export const taxService = new TaxService();
