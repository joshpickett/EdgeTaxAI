import React, { useState } from 'react';
import { UnifiedOCRService } from '../../../../services/unifiedOCRService';
import { DocumentCapture } from '../components/DocumentCapture';
import { COLORS } from '../../../../../assets/config/colors';
import { SPACING } from '../../../../../assets/config/spacing';
import { TYPOGRAPHY } from '../../../../../assets/config/typography';

interface GeneralIncomeStepProps {
  onUpdate: (data: any) => void;
  formData: any;
  onDocumentProcessed?: (result: any) => void;
}

interface ExtractedData {
  wages?: number;
  interest?: number;
  dividends?: number;
  otherIncome?: number;
  metadata?: Record<string, any>;
}

const GeneralIncomeStep: React.FC<GeneralIncomeStepProps> = ({ onUpdate, formData, onDocumentProcessed }) => {
  const [uploadedDocs, setUploadedDocs] = useState<any[]>([]);
  const [processing, setProcessing] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  
  const ocrService = new UnifiedOCRService();

  const handleDocumentUpload = async (file: File) => {
    setProcessing(true);
    try {
      const ocrResult = await ocrService.processDocument(file, 'general_income');
       
      if (ocrResult.success) {
        const extractedData: ExtractedData = ocrResult.data;
         
        const updatedData = {
          ...formData,
          wages: extractedData.wages || formData.wages,
          interest: extractedData.interest || formData.interest,
          dividends: extractedData.dividends || formData.dividends,
          otherIncome: extractedData.otherIncome || formData.otherIncome,
        };

        onUpdate(updatedData);
        onDocumentProcessed?.(ocrResult);
 
        setUploadedDocs([...uploadedDocs, {
          file,
          extractedData,
          timestamp: new Date().toISOString(),
          status: 'processed'
        }]);
      } else {
        setError(ocrResult.error || 'Failed to process document');
      }
    } catch (error) {
      console.error('Error processing document:', error);
      setError('Error processing document. Please try again.');
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>General Income Information</h2>
      
      <div style={styles.documentSection}>
        <DocumentCapture
          onUpload={handleDocumentUpload}
          onError={(err) => setError(err)}
          isProcessing={processing}
          acceptedTypes={['application/pdf', 'image/jpeg', 'image/png', 'image/gif']}
          maxSize={10 * 1024 * 1024} // 10MB
        />
        
        {error && (
          <div style={styles.error}>{error}</div>
        )}
      </div>
    </div>
  );
};

const styles = {
  container: {
    padding: SPACING.MEDIUM,
    backgroundColor: COLORS.WHITE,
    borderRadius: SPACING.SMALL,
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
  },
  title: {
    ...TYPOGRAPHY.HEADING,
    marginBottom: SPACING.SMALL,
  },
  documentSection: {
    marginTop: SPACING.MEDIUM,
  },
  error: {
    color: COLORS.RED,
    marginTop: SPACING.SMALL,
  },
};

export default GeneralIncomeStep;
