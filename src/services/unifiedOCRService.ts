import { Platform } from 'react-native';
import { 
  OCRResult, 
  DocumentType, 
  VerificationResult, 
  ProcessingOptions 
} from '../types/ocr';
import { OfflineQueueManager } from './offlineQueueManager';
import { PlatformDetector } from '../utils/platformDetector';
import { verificationService } from '../../shared/services/verificationService';

export class UnifiedOCRService {
  private offlineQueue: OfflineQueueManager;
  private platformDetector: PlatformDetector;
  private readonly confidenceThreshold = 0.8;
  private verificationService: typeof verificationService;

  constructor() {
    this.offlineQueue = new OfflineQueueManager();
    this.platformDetector = new PlatformDetector();
    this.verificationService = verificationService;
  }

  async processDocument(
    file: File | string,
    options: ProcessingOptions = {}
  ): Promise<OCRResult> {
    try {
      // Handle offline scenario
      if (!navigator.onLine) {
        await this.offlineQueue.addToQueue('processDocument', { file, options });
        return {
          status: 'queued',
          message: 'Document will be processed when online'
        };
      }

      const platform = this.platformDetector.getCurrentPlatform();
      const processedResult = await this.processForPlatform(file, platform, options);
      
      const enhancedResults = await this.validateAndEnhanceResults(processedResult);
      const verificationResults = await this.verificationService.verifyDocument(enhancedResults);
      return { ...enhancedResults, verificationResults };
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async verifyField(
    field: string,
    value: string,
    documentType: DocumentType
  ): Promise<VerificationResult> {
    try {
      const verificationRules = this.getVerificationRules(documentType);
      const result = await this.performVerification(field, value, verificationRules);
      
      return {
        isValid: result.isValid,
        confidence: result.confidence,
        suggestions: result.suggestions
      };
    } catch (error) {
      throw this.handleError(error);
    }
  }

  private async processForPlatform(
    file: File | string,
    platform: string,
    options: ProcessingOptions
  ): Promise<any> {
    switch (platform) {
      case 'mobile':
        return this.processMobileDocument(file, options);
      case 'web':
        return this.processWebDocument(file, options);
      default:
        throw new Error(`Unsupported platform: ${platform}`);
    }
  }

  private async processMobileDocument(
    file: string,
    options: ProcessingOptions
  ): Promise<any> {
    // Mobile-specific processing logic
    const imageProcessor = new MobileImageProcessor();
    const processedImage = await imageProcessor.prepare(file);
    return this.performOCR(processedImage, options);
  }

  private async processWebDocument(
    file: File,
    options: ProcessingOptions
  ): Promise<any> {
    // Web-specific processing logic
    const imageProcessor = new WebImageProcessor();
    const processedImage = await imageProcessor.prepare(file);
    return this.performOCR(processedImage, options);
  }

  private async performOCR(
    processedImage: any,
    options: ProcessingOptions
  ): Promise<any> {
    // Core OCR logic
    const result = await this.sendToOCREngine(processedImage);
    return this.enhanceResults(result, options);
  }

  private validateAndEnhanceResults(rawResults: any): OCRResult {
    const enhancedResults = {
      ...rawResults,
      fields: this.enhanceFields(rawResults.fields),
      confidence: this.calculateOverallConfidence(rawResults.fields),
      needsVerification: false,
      processedAt: new Date().toISOString()
    };

    enhancedResults.needsVerification = 
      enhancedResults.confidence < this.confidenceThreshold;

    return enhancedResults;
  }

  private enhanceFields(fields: Record<string, any>): Record<string, any> {
    return Object.entries(fields).reduce((acc, [key, value]) => {
      acc[key] = {
        value: value.text,
        confidence: value.confidence,
        needsVerification: value.confidence < this.confidenceThreshold,
        suggestions: value.alternatives || []
      };
      return acc;
    }, {});
  }

  private calculateOverallConfidence(fields: Record<string, any>): number {
    const confidences = Object.values(fields).map(f => f.confidence);
    return confidences.reduce((sum, conf) => sum + conf, 0) / confidences.length;
  }

  private handleError(error: any): Error {
    // Enhanced error handling
    console.error('OCR Error:', error);
    return new Error(`OCR processing failed: ${error.message}`);
  }
}

export const unifiedOCRService = new UnifiedOCRService();
