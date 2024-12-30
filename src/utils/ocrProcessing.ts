import { unifiedOCRService } from '../services/unifiedOCRService';
import { OCRResult, VerificationResult } from '../types/ocr';

export const processDocumentWithOCR = async (
  file: File,
  documentType: string,
  options: any = {}
): Promise<{
  result: OCRResult;
  verificationResults: VerificationResult[];
}> => {
  try {
    const result = await unifiedOCRService.processDocument(file, {
      documentType,
      enhanceResults: true,
      validateFields: true,
      ...options
    });

    return {
      result,
      verificationResults: result.verificationResults || []
    };
  } catch (error) {
    throw new Error(`OCR Processing failed: ${error.message}`);
  }
};

export const mapOCRResultsToW2Data = (result: OCRResult): any => {
  return {
    employerName: result.fields.employerName?.value,
    employerEIN: result.fields.employerEIN?.value,
    wages: parseFloat(result.fields.wages?.value || '0'),
    federalTaxWithheld: parseFloat(result.fields.federalTaxWithheld?.value || '0'),
    // ... map other fields
  };
};

export const mapOCRResultsToForm1099Data = (result: OCRResult): any => {
  return {
    payerName: result.fields.payerName?.value,
    payerTIN: result.fields.payerTIN?.value,
    amount: parseFloat(result.fields.amount?.value || '0'),
    federalTaxWithheld: parseFloat(result.fields.federalTaxWithheld?.value || '0'),
    // ... map other fields
  };
};

export const validateOCRResults = (
  results: OCRResult,
  requiredFields: string[]
): boolean => {
  return requiredFields.every(field => {
    const fieldData = results.fields[field];
    return fieldData && fieldData.confidence >= 0.8;
  });
};
