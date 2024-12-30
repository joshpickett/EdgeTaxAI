import React, { useState } from 'react';
import { formFieldStyles } from '../styles/FormFieldStyles';
import { formSectionStyles } from '../styles/FormSectionStyles';
import { DocumentCapture } from './DocumentCapture';
import { unifiedOCRService } from '../../../../services/unifiedOCRService';

interface W2Data {
  id: string;
  employerName: string;
  employerEIN: string;
  employerAddress: {
    street: string;
    city: string;
    state: string;
    zipCode: string;
  };
  wages: number;
  federalTaxWithheld: number;
  socialSecurityWages: number;
  socialSecurityTax: number;
  medicareWages: number;
  medicareTax: number;
  stateWages: number;
  stateTaxWithheld: number;
  localWages: number;
  localTaxWithheld: number;
}

interface W2FormProps {
  w2Data: W2Data;
  onUpdate: (data: W2Data) => void;
  onRemove: () => void;
}

export const W2Form: React.FC<W2FormProps> = ({
  w2Data,
  onUpdate,
  onRemove
}) => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [ocrError, setOcrError] = useState<string | null>(null);
  const [verificationResults, setVerificationResults] = useState<any[]>([]);

  const handleDocumentCapture = async (file: File) => {
    setIsProcessing(true);
    setOcrError(null);
    
    try {
      const result = await unifiedOCRService.processDocument(file, {
        documentType: 'W2',
        enhanceResults: true,
        validateFields: true
      });
      
      if (result.documentType !== 'W2') {
        throw new Error('Invalid document type. Please upload a W-2 form.');
      }
      
      setVerificationResults(result.verificationResults);

      // Update form with OCR results
      onUpdate({
        ...w2Data,
        ...mapOCRResultsToW2Data(result)
      });

      // Handle fields that need verification
      if (result.needsVerification) {
        handleVerificationNeeded(result.fields);
      }
    } catch (error) {
      setOcrError(error.message);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div style={formSectionStyles.container}>
      <DocumentCapture
        onCapture={handleDocumentCapture}
        onError={setOcrError}
      />
      
      {isProcessing && (
        <div style={formFieldStyles.processing}>
          Processing document...
        </div>
      )}
      
      {ocrError && (
        <div style={formFieldStyles.error}>
          {ocrError}
        </div>
      )}

      <div style={formFieldStyles.group}>
        <h4>Employer Information</h4>
        <div style={formFieldStyles.row}>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Employer Name</label>
            <input
              type="text"
              value={w2Data.employerName}
              onChange={(e) => handleChange('employerName', e.target.value)}
              style={formFieldStyles.input}
              required
            />
          </div>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Employer EIN</label>
            <input
              type="text"
              value={w2Data.employerEIN}
              onChange={(e) => handleChange('employerEIN', e.target.value)}
              style={formFieldStyles.input}
              pattern="\d{2}-\d{7}"
              placeholder="XX-XXXXXXX"
              required
            />
          </div>
        </div>

        <h4>Employer Address</h4>
        <div style={formFieldStyles.row}>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Street</label>
            <input
              type="text"
              value={w2Data.employerAddress.street}
              onChange={(e) => handleChange('employerAddress.street', e.target.value)}
              style={formFieldStyles.input}
              required
            />
          </div>
        </div>
        <div style={formFieldStyles.row}>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>City</label>
            <input
              type="text"
              value={w2Data.employerAddress.city}
              onChange={(e) => handleChange('employerAddress.city', e.target.value)}
              style={formFieldStyles.input}
              required
            />
          </div>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>State</label>
            <input
              type="text"
              value={w2Data.employerAddress.state}
              onChange={(e) => handleChange('employerAddress.state', e.target.value)}
              style={formFieldStyles.input}
              maxLength={2}
              required
            />
          </div>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>ZIP Code</label>
            <input
              type="text"
              value={w2Data.employerAddress.zipCode}
              onChange={(e) => handleChange('employerAddress.zipCode', e.target.value)}
              style={formFieldStyles.input}
              pattern="\d{5}(-\d{4})?"
              required
            />
          </div>
        </div>

        <h4>Income and Tax Information</h4>
        <div style={formFieldStyles.row}>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Wages (Box 1)</label>
            <input
              type="number"
              value={w2Data.wages}
              onChange={(e) => handleChange('wages', parseFloat(e.target.value))}
              style={formFieldStyles.input}
              min="0"
              step="0.01"
              required
            />
          </div>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Federal Tax Withheld (Box 2)</label>
            <input
              type="number"
              value={w2Data.federalTaxWithheld}
              onChange={(e) => handleChange('federalTaxWithheld', parseFloat(e.target.value))}
              style={formFieldStyles.input}
              min="0"
              step="0.01"
              required
            />
          </div>
        </div>

        <div style={formFieldStyles.row}>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Social Security Wages (Box 3)</label>
            <input
              type="number"
              value={w2Data.socialSecurityWages}
              onChange={(e) => handleChange('socialSecurityWages', parseFloat(e.target.value))}
              style={formFieldStyles.input}
              min="0"
              step="0.01"
            />
          </div>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Social Security Tax (Box 4)</label>
            <input
              type="number"
              value={w2Data.socialSecurityTax}
              onChange={(e) => handleChange('socialSecurityTax', parseFloat(e.target.value))}
              style={formFieldStyles.input}
              min="0"
              step="0.01"
            />
          </div>
        </div>

        <div style={formFieldStyles.row}>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Medicare Wages (Box 5)</label>
            <input
              type="number"
              value={w2Data.medicareWages}
              onChange={(e) => handleChange('medicareWages', parseFloat(e.target.value))}
              style={formFieldStyles.input}
              min="0"
              step="0.01"
            />
          </div>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Medicare Tax (Box 6)</label>
            <input
              type="number"
              value={w2Data.medicareTax}
              onChange={(e) => handleChange('medicareTax', parseFloat(e.target.value))}
              style={formFieldStyles.input}
              min="0"
              step="0.01"
            />
          </div>
        </div>

        <button
          onClick={onRemove}
          style={formFieldStyles.button.secondary}
        >
          Remove W-2
        </button>
      </div>
    </div>
  );

  const handleVerificationNeeded = (fields: any) => {
    // Show verification interface for fields that need review
    setVerificationResults(
      Object.entries(fields)
        .filter(([_, value]: any) => value.needsVerification)
        .map(([field, value]: any) => ({
          field,
          ...value
        }))
    );
  };
};
