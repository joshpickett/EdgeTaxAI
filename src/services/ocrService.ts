import { TaxDocument, OCRResult, FieldConfidence } from '../types/ocr';

export class OCRService {
  private readonly confidenceThreshold = 0.8;

  async processDocument(file: File): Promise<OCRResult> {
    try {
      const formData = new FormData();
      formData.append('document', file);

      const response = await fetch('/api/ocr/process', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error('OCR processing failed');
      }

      const result = await response.json();
      return this.validateAndFormatResults(result);
    } catch (error) {
      throw new Error(`OCR processing error: ${error.message}`);
    }
  }

  private validateAndFormatResults(rawResults: any): OCRResult {
    const fields: Record<string, FieldConfidence> = {};
    
    for (const [field, value] of Object.entries(rawResults.fields)) {
      fields[field] = {
        value: value.text,
        confidence: value.confidence,
        needsVerification: value.confidence < this.confidenceThreshold
      };
    }

    return {
      documentType: rawResults.documentType,
      fields,
      originalImage: rawResults.originalImage,
      processedAt: new Date().toISOString()
    };
  }

  async verifyField(field: string, value: string): Promise<boolean> {
    try {
      const response = await fetch('/api/ocr/verify', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ field, value })
      });

      if (!response.ok) {
        throw new Error('Field verification failed');
      }

      const result = await response.json();
      return result.isValid;
    } catch (error) {
      throw new Error(`Field verification error: ${error.message}`);
    }
  }
}

export const ocrService = new OCRService();
