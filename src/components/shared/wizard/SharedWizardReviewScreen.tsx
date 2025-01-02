import React, { useState } from 'react';
import { COLORS } from '../../../../assets/config/colors';
import { SPACING } from '../../../../assets/config/spacing';
import { TYPOGRAPHY } from '../../../../assets/config/typography';
import { DocumentType } from '../../../types/documents';

interface SharedWizardReviewScreenProps {
  documents: Array<{
    id: string;
    type: DocumentType;
    name: string;
    status: 'pending' | 'uploaded' | 'verified' | 'rejected';
    validationResults?: Array<{
      field: string;
      isValid: boolean;
      message?: string;
    }>;
    metadata?: Record<string, any>;
  }>;
  onSubmit: () => void;
  onBack: () => void;
  onReupload: (documentId: string) => void;
}

export const SharedWizardReviewScreen: React.FC<SharedWizardReviewScreenProps> = ({
  documents,
  onSubmit,
  onBack,
  onReupload
}) => {
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);

  const hasValidationErrors = documents.some(doc => 
    doc.validationResults?.some(result => !result.isValid)
  );

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'verified':
        return COLORS.success.main;
      case 'uploaded':
        return COLORS.primary;
      case 'rejected':
        return COLORS.error;
      default:
        return COLORS.text.secondary;
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h2 style={styles.title}>Review Documents</h2>
        <p style={styles.subtitle}>
          Please review your documents before final submission
        </p>
      </div>

      <div style={styles.documentList}>
        {documents.map(doc => (
          <div key={doc.id} style={styles.documentCard}>
            <div style={styles.documentHeader}>
              <h3 style={styles.documentName}>{doc.name}</h3>
              <span style={{
                ...styles.statusBadge,
                backgroundColor: getStatusColor(doc.status)
              }}>
                {doc.status}
              </span>
            </div>

            {doc.validationResults && (
              <div style={styles.validationResults}>
                {doc.validationResults.map((result, index) => (
                  <div 
                    key={index}
                    style={{
                      ...styles.validationItem,
                      color: result.isValid ? COLORS.success.main : COLORS.error
                    }}
                  >
                    <span>{result.field}:</span>
                    {result.message && <span>{result.message}</span>}
                  </div>
                ))}
              </div>
            )}

            {doc.metadata && (
              <div style={styles.metadata}>
                <h4 style={styles.metadataTitle}>Extracted Information</h4>
                {Object.entries(doc.metadata).map(([key, value]) => (
                  <div key={key} style={styles.metadataItem}>
                    <span style={styles.metadataKey}>{key}:</span>
                    <span style={styles.metadataValue}>{value}</span>
                  </div>
                ))}
              </div>
            )}

            {doc.status === 'rejected' && (
              <button
                onClick={() => onReupload(doc.id)}
                style={styles.reuploadButton}
              >
                Reupload Document
              </button>
            )}
          </div>
        ))}
      </div>

      <div style={styles.navigation}>
        <button 
          onClick={onBack}
          style={styles.backButton}
        >
          Back
        </button>
        <button
          onClick={() => setShowConfirmDialog(true)}
          style={styles.submitButton}
          disabled={hasValidationErrors}
        >
          Submit Documents
        </button>
      </div>

      {showConfirmDialog && (
        <div style={styles.confirmDialog}>
          <div style={styles.dialogContent}>
            <h3>Confirm Submission</h3>
            <p>Are you sure you want to submit these documents?</p>
            <div style={styles.dialogButtons}>
              <button
                onClick={() => setShowConfirmDialog(false)}
                style={styles.cancelButton}
              >
                Cancel
              </button>
              <button
                onClick={onSubmit}
                style={styles.confirmButton}
              >
                Confirm
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const styles = {
  container: {
    padding: SPACING.xl,
    maxWidth: '800px',
    margin: '0 auto'
  },
  header: {
    marginBottom: SPACING.xl
  },
  title: {
    fontSize: TYPOGRAPHY.fontSize.xl,
    fontFamily: TYPOGRAPHY.fontFamily.bold,
    color: COLORS.text.primary,
    marginBottom: SPACING.sm
  },
  subtitle: {
    fontSize: TYPOGRAPHY.fontSize.md,
    color: COLORS.text.secondary
  },
  documentList: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: SPACING.md
  },
  documentCard: {
    backgroundColor: COLORS.surface,
    borderRadius: '8px',
    padding: SPACING.lg,
    border: `1px solid ${COLORS.border}`
  },
  documentHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: SPACING.md
  },
  documentName: {
    fontSize: TYPOGRAPHY.fontSize.lg,
    fontFamily: TYPOGRAPHY.fontFamily.medium,
    color: COLORS.text.primary,
    margin: 0
  },
  statusBadge: {
    padding: `${SPACING.xs}px ${SPACING.sm}px`,
    borderRadius: '4px',
    color: COLORS.background,
    fontSize: TYPOGRAPHY.fontSize.sm
  },
  validationResults: {
    marginTop: SPACING.md,
    padding: SPACING.md,
    backgroundColor: COLORS.background,
    borderRadius: '4px'
  },
  validationItem: {
    display: 'flex',
    justifyContent: 'space-between',
    marginBottom: SPACING.xs
  },
  metadata: {
    marginTop: SPACING.md,
    padding: SPACING.md,
    backgroundColor: COLORS.background,
    borderRadius: '4px'
  },
  metadataTitle: {
    fontSize: TYPOGRAPHY.fontSize.md,
    fontFamily: TYPOGRAPHY.fontFamily.medium,
    color: COLORS.text.primary,
    marginBottom: SPACING.sm
  },
  metadataItem: {
    display: 'flex',
    marginBottom: SPACING.xs
  },
  metadataKey: {
    color: COLORS.text.secondary,
    marginRight: SPACING.sm,
    minWidth: '120px'
  },
  metadataValue: {
    color: COLORS.text.primary
  },
  reuploadButton: {
    marginTop: SPACING.md,
    padding: `${SPACING.sm}px ${SPACING.md}px`,
    backgroundColor: COLORS.surface,
    border: `1px solid ${COLORS.border}`,
    borderRadius: '4px',
    cursor: 'pointer',
    color: COLORS.text.primary
  },
  navigation: {
    display: 'flex',
    justifyContent: 'space-between',
    marginTop: SPACING.xl,
    paddingTop: SPACING.lg,
    borderTop: `1px solid ${COLORS.border}`
  },
  backButton: {
    backgroundColor: COLORS.surface,
    color: COLORS.text.primary,
    border: `1px solid ${COLORS.border}`,
    padding: `${SPACING.sm}px ${SPACING.md}px`,
    borderRadius: '4px',
    cursor: 'pointer'
  },
  submitButton: {
    backgroundColor: COLORS.primary,
    color: COLORS.background,
    border: 'none',
    padding: `${SPACING.sm}px ${SPACING.md}px`,
    borderRadius: '4px',
    cursor: 'pointer',
    '&:disabled': {
      backgroundColor: COLORS.text.disabled,
      cursor: 'not-allowed'
    }
  },
  confirmDialog: {
    position: 'fixed' as const,
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center'
  },
  dialogContent: {
    backgroundColor: COLORS.background,
    padding: SPACING.xl,
    borderRadius: '8px',
    maxWidth: '400px',
    width: '100%'
  },
  dialogButtons: {
    display: 'flex',
    justifyContent: 'flex-end',
    gap: SPACING.md,
    marginTop: SPACING.lg
  },
  cancelButton: {
    backgroundColor: COLORS.surface,
    color: COLORS.text.primary,
    border: `1px solid ${COLORS.border}`,
    padding: `${SPACING.sm}px ${SPACING.md}px`,
    borderRadius: '4px',
    cursor: 'pointer'
  },
  confirmButton: {
    backgroundColor: COLORS.primary,
    color: COLORS.background,
    border: 'none',
    padding: `${SPACING.sm}px ${SPACING.md}px`,
    borderRadius: '4px',
    cursor: 'pointer'
  }
};
