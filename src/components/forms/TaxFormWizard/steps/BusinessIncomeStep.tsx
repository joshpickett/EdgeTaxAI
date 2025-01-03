import React, { useState } from 'react';
import { DocumentCapture } from '../components/DocumentCapture';
import { UnifiedOCRService } from '../../../../services/unifiedOCRService';
import { COLORS } from '../../../../../assets/config/colors';
import { SPACING } from '../../../../../assets/config/spacing';
import { TYPOGRAPHY } from '../../../../../assets/config/typography';

interface BusinessIncomeStepProps {
  onUpdate: (data: any) => void;
  formData: any;
  onDocumentProcessed?: (result: any) => void;
}

export const BusinessIncomeStep: React.FC<BusinessIncomeStepProps> = ({
  onUpdate,
  formData,
  onDocumentProcessed
}) => {
  const [processing, setProcessing] = useState(false);
  const [uploadedDocs, setUploadedDocs] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);
  const ocrService = new UnifiedOCRService();

  const handleDocumentUpload = async (file: File) => {
    setProcessing(true);
    try {
      const ocrResult = await ocrService.processDocument(file, 'business_income');
      
      if (ocrResult.success) {
        const extractedData = ocrResult.data;
        
        onUpdate({
          ...formData,
          businessIncome: extractedData.businessIncome || formData.businessIncome,
          platform1099K: extractedData.platform1099K || formData.platform1099K,
          platform1099NEC: extractedData.platform1099NEC || formData.platform1099NEC
        });

        setUploadedDocs([...uploadedDocs, {
          file,
          extractedData,
          timestamp: new Date().toISOString(),
          status: 'processed'
        }]);

        onDocumentProcessed?.(ocrResult);
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
      <h2 style={styles.title}>Business Income Information</h2>
      
      <div style={styles.section}>
        <h3 style={styles.subtitle}>Business Activities</h3>
        <div style={styles.formGroup}>
          <label style={styles.label}>
            Business Income
            <input
              type="number"
              value={formData.businessIncome || ''}
              onChange={(e) => onUpdate({
                ...formData,
                businessIncome: parseFloat(e.target.value)
              })}
              style={styles.input}
            />
          </label>
        </div>
      </div>

      <div style={styles.section}>
        <h3 style={styles.subtitle}>Third-Party Payment Processors</h3>
        <div style={styles.formGroup}>
          <label style={styles.label}>
            1099-K Income
            <input
              type="number"
              value={formData.platform1099K || ''}
              onChange={(e) => onUpdate({
                ...formData,
                platform1099K: parseFloat(e.target.value)
              })}
              style={styles.input}
            />
          </label>
        </div>
        <div style={styles.formGroup}>
          <label style={styles.label}>
            1099-NEC Income
            <input
              type="number"
              value={formData.platform1099NEC || ''}
              onChange={(e) => onUpdate({
                ...formData,
                platform1099NEC: parseFloat(e.target.value)
              })}
              style={styles.input}
            />
          </label>
        </div>
      </div>
      
      <div style={styles.uploadSection}>
        <h3 style={styles.subtitle}>Upload Documents</h3>
        <p style={styles.helpText}>
          Upload your 1099-K, 1099-NEC, or other business income documents
        </p>
        <DocumentCapture
          onCapture={handleDocumentUpload}
          onError={(err) => setError(err)}
          isProcessing={processing}
          acceptedTypes={['application/pdf', 'image/jpeg', 'image/png']}
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
    padding: SPACING.lg
  },
  title: {
    fontSize: TYPOGRAPHY.fontSize.xl,
    fontFamily: TYPOGRAPHY.fontFamily.bold,
    color: COLORS.text.primary,
    marginBottom: SPACING.lg
  },
  subtitle: {
    fontSize: TYPOGRAPHY.fontSize.lg,
    fontFamily: TYPOGRAPHY.fontFamily.medium,
    color: COLORS.text.primary,
    marginBottom: SPACING.md
  },
  section: {
    marginBottom: SPACING.xl
  },
  formGroup: {
    marginBottom: SPACING.md
  },
  label: {
    display: 'block',
    fontSize: TYPOGRAPHY.fontSize.md,
    color: COLORS.text.primary,
    marginBottom: SPACING.xs
  },
  input: {
    width: '100%',
    padding: SPACING.sm,
    fontSize: TYPOGRAPHY.fontSize.md,
    border: `1px solid ${COLORS.border}`,
    borderRadius: '4px',
    marginTop: SPACING.xs
  },
  uploadSection: {
    marginTop: SPACING.xl,
    padding: SPACING.lg,
    backgroundColor: COLORS.surface,
    borderRadius: '8px'
  },
  helpText: {
    fontSize: TYPOGRAPHY.fontSize.md,
    color: COLORS.text.secondary,
    marginBottom: SPACING.md
  },
  error: {
    color: COLORS.error,
    fontSize: TYPOGRAPHY.fontSize.md,
    marginTop: SPACING.sm
  }
};
