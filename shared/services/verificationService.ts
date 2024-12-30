import { OCRResult, VerificationResult, FieldConfidence } from '../types/ocr';
import { errorHandler } from './errorHandler';
import { ApiClient } from './apiClient';
import { OfflineQueueManager } from './offlineQueueManager';

export class VerificationService {
  private apiClient: ApiClient;
  private offlineQueue: OfflineQueueManager;
  private readonly confidenceThreshold = 0.8;

  constructor() {
    this.apiClient = new ApiClient();
    this.offlineQueue = new OfflineQueueManager();
  }

  async verifyField(field: string, value: string, context?: any): Promise<VerificationResult> {
    try {
      // Check offline queue first
      if (!navigator.onLine) {
        await this.offlineQueue.addToQueue('verifyField', { field, value, context });
        return {
          isValid: true,
          confidence: 0.5,
          needsManualReview: true,
          message: 'Queued for verification when online'
        };
      }

      const result = await this.apiClient.post('/verify/field', {
        field,
        value,
        context
      });

      return this.processVerificationResult(result);
    } catch (error) {
      errorHandler.handleError(error, {
        component: 'VerificationService',
        operation: 'verifyField',
        retryCount: 0,
        maxRetries: 3
      });
      throw error;
    }
  }

  async verifyDocument(ocrResult: OCRResult): Promise<VerificationResult[]> {
    try {
      const verificationResults: VerificationResult[] = [];

      for (const [field, value] of Object.entries(ocrResult.fields)) {
        const result = await this.verifyField(field, value.value, {
          documentType: ocrResult.documentType,
          confidence: value.confidence
        });
        verificationResults.push(result);
      }

      return verificationResults;
    } catch (error) {
      errorHandler.handleError(error, {
        component: 'VerificationService',
        operation: 'verifyDocument',
        retryCount: 0,
        maxRetries: 3
      });
      throw error;
    }
  }

  private processVerificationResult(result: any): VerificationResult {
    return {
      isValid: result.confidence >= this.confidenceThreshold,
      confidence: result.confidence,
      needsManualReview: result.confidence < this.confidenceThreshold,
      suggestions: result.suggestions || [],
      message: result.message || ''
    };
  }

  async validateFieldFormat(field: string, value: string): Promise<boolean> {
    const formatRules = {
      ssn: /^\d{3}-?\d{2}-?\d{4}$/,
      ein: /^\d{2}-?\d{7}$/,
      phone: /^\d{3}-?\d{3}-?\d{4}$/,
      email: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
      zipCode: /^\d{5}(-\d{4})?$/
    };

    const rule = formatRules[field];
    return rule ? rule.test(value) : true;
  }
}

export const verificationService = new VerificationService();
