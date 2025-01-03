import { OpticalCharacterRecognitionService } from './opticalCharacterRecognitionService';
import { DocumentValidationService } from './documentValidationService';
import { DocumentType } from '../types/documents';

interface OpticalCharacterRecognitionResult {
  success: boolean;
  data: {
    wages?: number;
    interest?: number;
    dividends?: number;
    otherIncome?: number;
    freelanceIncome?: number;
    contractorPayments?: number;
    homeOfficeExpenses?: number;
    totalHomeSquareFootage?: number;
    officeSquareFootage?: number;
    metadata?: Record<string, any>;
  };
  error?: string;
}

export class UnifiedOpticalCharacterRecognitionService {
  private opticalCharacterRecognitionService: OpticalCharacterRecognitionService;
  private validationService: DocumentValidationService;

  constructor() {
    this.opticalCharacterRecognitionService = new OpticalCharacterRecognitionService();
    this.validationService = new DocumentValidationService();
  }

  async processDocument(file: File, context: string): Promise<OpticalCharacterRecognitionResult> {
    try {
      // Validate document first
      const validationResult = await this.validationService.validateDocument(file);
      if (!validationResult.isValid) {
        return {
          success: false,
          data: {},
          error: validationResult.error
        };
      }

      // Process with Optical Character Recognition
      const opticalCharacterRecognitionResult = await this.opticalCharacterRecognitionService.processDocument(file);
      
      if (!opticalCharacterRecognitionResult.success) {
        return {
          success: false,
          data: {},
          error: 'Failed to process document with Optical Character Recognition'
        };
      }

      // Extract relevant information based on context
      const extractedData = this.extractRelevantData(opticalCharacterRecognitionResult.data, context);

      return {
        success: true,
        data: {
          ...extractedData,
          documentType: this.determineDocumentType(opticalCharacterRecognitionResult.data),
          metadata: opticalCharacterRecognitionResult.metadata
        }
      };

    } catch (error) {
      console.error('Error in unified Optical Character Recognition processing:', error);
      return {
        success: false,
        data: {},
        error: 'Error processing document'
      };
    }
  }

  private extractRelevantData(opticalCharacterRecognitionData: any, context: string): Record<string, any> {
    switch (context) {
      case 'income':
      case 'general_income':
        return {
          wages: this.extractNumeric(opticalCharacterRecognitionData.wages || opticalCharacterRecognitionData.salary),
          interest: this.extractNumeric(opticalCharacterRecognitionData.interest),
          dividends: this.extractNumeric(opticalCharacterRecognitionData.dividends),
          otherIncome: this.extractNumeric(opticalCharacterRecognitionData.otherIncome)
        };
      case 'freelance_income':
        return {
          freelanceIncome: this.extractNumeric(opticalCharacterRecognitionData.freelanceIncome || opticalCharacterRecognitionData.nonemployeeCompensation),
          contractorPayments: this.extractNumeric(opticalCharacterRecognitionData.contractorPayments),
          homeOfficeExpenses: this.extractNumeric(opticalCharacterRecognitionData.homeOfficeExpenses),
          totalHomeSquareFootage: this.extractNumeric(opticalCharacterRecognitionData.totalHomeSquareFootage),
          officeSquareFootage: this.extractNumeric(opticalCharacterRecognitionData.officeSquareFootage),
          businessUsePercentage: this.calculateBusinessUsePercentage(opticalCharacterRecognitionData)
        };
      default:
        return {};
    }
  }

  private extractNumeric(value: any): number | undefined {
    if (!value) return undefined;
    const numeric = parseFloat(value.toString().replace(/[^0-9.-]+/g, ''));
    return isNaN(numeric) ? undefined : numeric;
  }

  private calculateBusinessUsePercentage(data: any): number | undefined {
    const total = this.extractNumeric(data.totalHomeSquareFootage);
    const office = this.extractNumeric(data.officeSquareFootage);
    
    if (total && office && total > 0) {
      return (office / total) * 100;
    }
    return undefined;
  }

  private determineDocumentType(opticalCharacterRecognitionData: any): DocumentType {
    // Logic to determine document type based on Optical Character Recognition data
    if (opticalCharacterRecognitionData.formType === 'W-2') return DocumentType.W2;
    if (opticalCharacterRecognitionData.formType === '1099-INT') return DocumentType.FORM_1099;
    if (opticalCharacterRecognitionData.formType === '1099-DIV') return DocumentType.FORM_1099;
    if (opticalCharacterRecognitionData.formType === '1099-MISC') return DocumentType.FORM_1099;
    if (opticalCharacterRecognitionData.formType === '1099-NEC') return DocumentType.FORM_1099_NEC;
    if (opticalCharacterRecognitionData.formType === '1099-K') return DocumentType.FORM_1099K;
    // Add more document type detection logic
    return DocumentType.OTHER;
  }
}
