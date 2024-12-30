import React, { useState } from 'react';
import { formFieldStyles } from '../styles/FormFieldStyles';
import { formSectionStyles } from '../styles/FormSectionStyles';
import { DocumentCapture } from './DocumentCapture';
import { unifiedOCRService } from '../../../../services/unifiedOCRService';

interface Form1099Data {
  id: string;
  type: '1099-NEC' | '1099-K' | '1099-MISC';
  payerName: string;
  payerTIN: string;
  amount: number;
  federalTaxWithheld: number;
  stateTaxWithheld: number;
  platform?: string;
}

interface Form1099SectionProps {
  form1099Data: Form1099Data;
  onUpdate: (data: Form1099Data) => void;
  onRemove: () => void;
}

export const Form1099Section: React.FC<Form1099SectionProps> = ({
  form1099Data,
  onUpdate,
  onRemove
}) => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [ocrError, setOcrError] = useState<string | null>(null);
  const [verificationResults, setVerificationResults] = useState<any[]>([]);

  const handleChange = (field: string, value: any) => {
    onUpdate({
      ...form1099Data,
      [field]: value
    });
  };

  const handleDocumentCapture = async (file: File) => {
    setIsProcessing(true);
    setOcrError(null);
    
    try {
      const result = await unifiedOCRService.processDocument(file, {
        documentType: form1099Data.type,
        enhanceResults: true,
        validateFields: true
      });
      
      if (!result.documentType.includes('1099')) {
        throw new Error('Invalid document type. Please upload a 1099 form.');
      }
      
      setVerificationResults(result.verificationResults);
      
      onUpdate({
        ...form1099Data,
        ...mapOCRResultsToForm1099Data(result)
      });
    } catch (error) {
      setOcrError(error.message);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div style={formSectionStyles.container}>
      <div style={formFieldStyles.group}>
        <div style={formFieldStyles.row}>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Form Type</label>
            <select
              value={form1099Data.type}
              onChange={(e) => handleChange('type', e.target.value)}
              style={formFieldStyles.select}
              required
            >
              <option value="1099-NEC">1099-NEC</option>
              <option value="1099-K">1099-K</option>
              <option value="1099-MISC">1099-MISC</option>
            </select>
          </div>
          {form1099Data.type === '1099-K' && (
            <div style={formFieldStyles.column}>
              <label style={formFieldStyles.label}>Platform</label>
              <input
                type="text"
                value={form1099Data.platform}
                onChange={(e) => handleChange('platform', e.target.value)}
                style={formFieldStyles.input}
              />
            </div>
          )}
        </div>

        <div style={formFieldStyles.row}>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Payer Name</label>
            <input
              type="text"
              value={form1099Data.payerName}
              onChange={(e) => handleChange('payerName', e.target.value)}
              style={formFieldStyles.input}
              required
            />
          </div>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Payer TIN</label>
            <input
              type="text"
              value={form1099Data.payerTIN}
              onChange={(e) => handleChange('payerTIN', e.target.value)}
              style={formFieldStyles.input}
              pattern="\d{2}-\d{7}"
              placeholder="XX-XXXXXXX"
              required
            />
          </div>
        </div>

        <div style={formFieldStyles.row}>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Amount</label>
            <input
              type="number"
              value={form1099Data.amount}
              onChange={(e) => handleChange('amount', parseFloat(e.target.value))}
              style={formFieldStyles.input}
              min="0"
              step="0.01"
              required
            />
          </div>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Federal Tax Withheld</label>
            <input
              type="number"
              value={form1099Data.federalTaxWithheld}
              onChange={(e) => handleChange('federalTaxWithheld', parseFloat(e.target.value))}
              style={formFieldStyles.input}
              min="0"
              step="0.01"
            />
          </div>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>State Tax Withheld</label>
            <input
              type="number"
              value={form1099Data.stateTaxWithheld}
              onChange={(e) => handleChange('stateTaxWithheld', parseFloat(e.target.value))}
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
          Remove 1099
        </button>
      </div>
      
      <DocumentCapture
        onCapture={handleDocumentCapture}
        onError={setOcrError}
        acceptedTypes={['image/jpeg', 'image/png', 'application/pdf']}
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
    </div>
  );
};
