import React, { useState } from 'react';
import { DocumentCapture } from '../components/DocumentCapture';
import { UnifiedOCRService } from '../../../../services/unifiedOCRService';
import { COLORS } from '../../../../../assets/config/colors';
import { SPACING } from '../../../../../assets/config/spacing';
import { TYPOGRAPHY } from '../../../../../assets/config/typography';

interface FreelanceIncomeStepProps {
  onUpdate: (data: any) => void;
  formData: any;
  onDocumentProcessed?: (result: any) => void;
}

export const FreelanceIncomeStep: React.FC<FreelanceIncomeStepProps> = ({
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
      const ocrResult = await ocrService.processDocument(file, 'freelance_income');
      
      if (ocrResult.success) {
        const extractedData = ocrResult.data;
        
        onUpdate({
          ...formData,
          freelanceIncome: extractedData.freelanceIncome || formData.freelanceIncome,
          contractorPayments: extractedData.contractorPayments || formData.contractorPayments,
          homeOfficeExpenses: extractedData.homeOfficeExpenses || formData.homeOfficeExpenses
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
      <h2 style={styles.title}>Freelance Income Information</h2>
      
      <div style={styles.section}>
        <h3 style={styles.subtitle}>Freelance/Contractor Income</h3>
        <div style={styles.formGroup}>
          <label style={styles.label}>
            Total Freelance Income
            <input
              type="number"
              value={formData.freelanceIncome || ''}
              onChange={(e) => onUpdate({
                ...formData,
                freelanceIncome: parseFloat(e.target.value)
              })}
              style={styles.input}
            />
          </label>
        </div>

        <div style={styles.formGroup}>
          <label style={styles.label}>
            Contractor Payments
            <input
              type="number"
              value={formData.contractorPayments || ''}
              onChange={(e) => onUpdate({
                ...formData,
                contractorPayments: parseFloat(e.target.value)
              })}
              style={styles.input}
            />
          </label>
        </div>
      </div>

      <div style={styles.section}>
        <h3 style={styles.subtitle}>Home Office Information</h3>
        <div style={styles.formGroup}>
          <label style={styles.label}>
            Total Square Footage of Home
            <input
              type="number"
              value={formData.totalHomeSquareFootage || ''}
              onChange={(e) => onUpdate({
                ...formData,
                totalHomeSquareFootage: parseFloat(e.target.value)
              })}
              style={styles.input}
            />
          </label>
        </div>

        <div style={styles.formGroup}>
          <label style={styles.label}>
            Square Footage of Home Office
            <input
              type="number"
              value={formData.officeSquareFootage || ''}
              onChange={(e) => onUpdate({
                ...formData,
                officeSquareFootage: parseFloat(e.target.value)
              })}
              style={styles.input}
            />
          </label>
        </div>

        <div style={styles.formGroup}>
          <label style={styles.label}>
            Home Office Expenses
            <input
              type="number"
              value={formData.homeOfficeExpenses || ''}
              onChange={(e) => onUpdate({
                ...formData,
                homeOfficeExpenses: parseFloat(e.target.value)
              })}
              style={styles.input}
            />
          </label>
        </div>
      </div>

      <div style={styles.uploadSection}>
        <h3 style={styles.subtitle}>Upload Documents</h3>
        <p style={styles.helpText}>
          Upload your 1099-NEC, contracts, or other freelance income documentation
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

        {uploadedDocs.length > 0 && (
          <div style={styles.uploadedDocs}>
            <h4 style={styles.uploadedTitle}>Uploaded Documents</h4>
            {uploadedDocs.map((doc, index) => (
              <div key={index} style={styles.docItem}>
                <span style={styles.docName}>{doc.file.name}</span>
                <span style={styles.docTimestamp}>
                  {new Date(doc.timestamp).toLocaleString()}
                </span>
              </div>
            ))}
          </div>
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
  },
  uploadedDocs: {
    marginTop: SPACING.lg
  },
  uploadedTitle: {
    fontSize: TYPOGRAPHY.fontSize.md,
    fontFamily: TYPOGRAPHY.fontFamily.medium,
    color: COLORS.text.primary,
    marginBottom: SPACING.sm
  },
  docItem: {
    display: 'flex',
    justifyContent: 'space-between',
    padding: SPACING.sm,
    backgroundColor: COLORS.background,
    borderRadius: '4px',
    marginBottom: SPACING.xs
  },
  docName: {
    fontSize: TYPOGRAPHY.fontSize.md,
    color: COLORS.text.primary
  },
  docTimestamp: {
    fontSize: TYPOGRAPHY.fontSize.sm,
    color: COLORS.text.secondary
  }
};
