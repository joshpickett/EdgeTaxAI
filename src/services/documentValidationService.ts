import { OCRService } from './ocrService';
import { VerificationService } from './verificationService';

interface ValidationResult {
  isValid: boolean;
  error?: string;
  metadata?: Record<string, any>;
}

export class DocumentValidationService {
  private ocrService: OCRService;
  private verificationService: VerificationService;

  constructor() {
    this.ocrService = new OCRService();
    this.verificationService = new VerificationService();
  }

  async validateDocument(
    file: File, 
    onProgress?: (progress: number) => void
  ): Promise<ValidationResult> {
    try {
      // Basic file validation
      if (!this.isValidFileType(file)) {
        return {
          isValid: false,
          error: 'Invalid file type'
        };
      }

      // OCR Processing
      onProgress?.(20);
      const ocrResult = await this.ocrService.processDocument(file);
      
      if (!ocrResult.success) {
        return {
          isValid: false,
          error: 'Failed to process document content'
        };
      }

      // Content verification
      onProgress?.(60);
      const verificationResult = await this.verificationService.verifyDocument(ocrResult);
      
      if (!verificationResult.isValid) {
        return {
          isValid: false,
          error: verificationResult.message
        };
      }

      onProgress?.(100);
      return {
        isValid: true,
        metadata: {
          ...ocrResult.data,
          verificationScore: verificationResult.confidence
        }
      };
    } catch (error) {
      console.error('Document validation error:', error);
      return {
        isValid: false,
        error: 'Error validating document'
      };
    }
  }

  private isValidFileType(file: File): boolean {
    const validTypes = [
      'application/pdf',
      'image/jpeg',
      'image/png'
    ];
    return validTypes.includes(file.type);
  }

  private async validateImageQuality(file: File): Promise<boolean> {
    if (!file.type.startsWith('image/')) {
      return true;
    }

    return new Promise((resolve) => {
      const img = new Image();
      img.onload = () => {
        const { width, height } = img;
        resolve(width >= 800 && height >= 600);
      };
      img.onerror = () => resolve(false);
      img.src = URL.createObjectURL(file);
    });
  }
}
