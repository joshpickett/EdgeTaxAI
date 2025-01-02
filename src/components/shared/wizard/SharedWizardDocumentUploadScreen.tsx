import React, { useState } from 'react';
import { COLORS } from '../../../../assets/config/colors';
import { SPACING } from '../../../../assets/config/spacing';
import { TYPOGRAPHY } from '../../../../assets/config/typography';
import { DocumentType } from '../../../types/documents';
import { DocumentUploader } from '../../DocumentCollection/DocumentUploader';
import { DocumentList } from '../../DocumentCollection/DocumentList';

interface SharedWizardDocumentUploadScreenProps {
  requiredDocuments: Array<{
    id: string;
    type: DocumentType;
    name: string;
    description: string;
    required: boolean;
    status?: 'pending' | 'uploaded' | 'verified' | 'rejected';
  }>;
  onUpload: (file: File, documentId: string) => Promise<void>;
  onComplete: () => void;
  onBack: () => void;
}

export const SharedWizardDocumentUploadScreen: React.FC<SharedWizardDocumentUploadScreenProps> = ({
  requiredDocuments,
  onUpload,
  onComplete,
  onBack
}) => {
  const [selectedDocument, setSelectedDocument] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  const handleUpload = async (file: File) => {
    if (!selectedDocument) return;
    
    setIsUploading(true);
    try {
      await onUpload(file, selectedDocument);
    } catch (error) {
      console.error('Upload error:', error);
    } finally {
      setIsUploading(false);
    }
  };

  const canComplete = requiredDocuments.every(doc => 
    !doc.required || ['uploaded', 'verified'].includes(doc.status || '')
  );

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h2 style={styles.title}>Upload Documents</h2>
        <p style={styles.subtitle}>
          Select each required document and upload the corresponding file
        </p>
      </div>

      <div style={styles.content}>
        <div style={styles.documentList}>
          {requiredDocuments.map(doc => (
            <div 
              key={doc.id}
              style={{
                ...styles.documentItem,
                ...(selectedDocument === doc.id ? styles.selectedDocument : {})
              }}
              onClick={() => setSelectedDocument(doc.id)}
            >
              <div style={styles.documentInfo}>
                <h3 style={styles.documentName}>{doc.name}</h3>
                {doc.required && (
                  <span style={styles.requiredBadge}>Required</span>
                )}
              </div>
              <div style={styles.documentStatus}>
                {doc.status && (
                  <span style={{
                    ...styles.statusBadge,
                    backgroundColor: getStatusColor(doc.status)
                  }}>
                    {doc.status}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>

        <div style={styles.uploadSection}>
          {selectedDocument ? (
            <DocumentUploader
              onUpload={handleUpload}
              isProcessing={isUploading}
              acceptedTypes={['application/pdf', 'image/jpeg', 'image/png']}
              maxSize={10 * 1024 * 1024} // 10MB
            />
          ) : (
            <div style={styles.uploadPrompt}>
              Select a document from the list to upload
            </div>
          )}
        </div>
      </div>

      <div style={styles.navigation}>
        <button 
          onClick={onBack}
          style={styles.backButton}
        >
          Back
        </button>
        <button
          onClick={onComplete}
          style={styles.continueButton}
          disabled={!canComplete}
        >
          Complete Upload
        </button>
      </div>
    </div>
  );
};

const getStatusColor = (status: string): string => {
  switch (status) {
    case 'verified':
      return '#4CAF50';
    case 'uploaded':
      return '#2196F3';
    case 'rejected':
      return '#F44336';
    default:
      return '#9E9E9E';
  }
};

const styles = {
  container: {
    padding: SPACING.xl,
    maxWidth: '1200px',
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
  content: {
    display: 'flex',
    gap: SPACING.xl,
    marginBottom: SPACING.xl
  },
  documentList: {
    flex: '0 0 300px',
    borderRight: `1px solid ${COLORS.border}`,
    paddingRight: SPACING.lg
  },
  documentItem: {
    padding: SPACING.md,
    borderRadius: '8px',
    marginBottom: SPACING.sm,
    cursor: 'pointer',
    transition: 'background-color 0.2s ease',
    '&:hover': {
      backgroundColor: COLORS.surface
    }
  },
  selectedDocument: {
    backgroundColor: COLORS.surface,
    border: `2px solid ${COLORS.primary}`
  },
  documentInfo: {
    display: 'flex',
    alignItems: 'center',
    gap: SPACING.sm,
    marginBottom: SPACING.xs
  },
  documentName: {
    fontSize: TYPOGRAPHY.fontSize.md,
    fontFamily: TYPOGRAPHY.fontFamily.medium,
    color: COLORS.text.primary,
    margin: 0
  },
  requiredBadge: {
    backgroundColor: COLORS.error,
    color: COLORS.background,
    padding: `${SPACING.xs}px ${SPACING.sm}px`,
    borderRadius: '4px',
    fontSize: TYPOGRAPHY.fontSize.xs
  },
  documentStatus: {
    display: 'flex',
    alignItems: 'center'
  },
  statusBadge: {
    padding: `${SPACING.xs}px ${SPACING.sm}px`,
    borderRadius: '4px',
    color: COLORS.background,
    fontSize: TYPOGRAPHY.fontSize.xs,
    textTransform: 'capitalize' as const
  },
  uploadSection: {
    flex: 1,
    padding: SPACING.lg,
    backgroundColor: COLORS.surface,
    borderRadius: '8px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center'
  },
  uploadPrompt: {
    color: COLORS.text.secondary,
    fontSize: TYPOGRAPHY.fontSize.lg,
    textAlign: 'center' as const
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
    cursor: 'pointer',
    fontSize: TYPOGRAPHY.fontSize.md,
    '&:hover': {
      backgroundColor: COLORS.background
    }
  },
  continueButton: {
    backgroundColor: COLORS.primary,
    color: COLORS.background,
    border: 'none',
    padding: `${SPACING.sm}px ${SPACING.md}px`,
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: TYPOGRAPHY.fontSize.md,
    '&:disabled': {
      backgroundColor: COLORS.text.disabled,
      cursor: 'not-allowed'
    },
    '&:hover:not(:disabled)': {
      backgroundColor: COLORS.secondary
    }
  }
};
