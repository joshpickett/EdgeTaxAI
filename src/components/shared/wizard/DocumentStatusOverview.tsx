import React from 'react';
import { COLORS } from '../../../../assets/config/colors';
import { SPACING } from '../../../../assets/config/spacing';
import { TYPOGRAPHY } from '../../../../assets/config/typography';
import { DocumentType } from '../../../types/documents';

interface DocumentStatusOverviewProps {
  documents: Array<{
    id: string;
    type: DocumentType;
    name: string;
    description: string;
    required: boolean;
    status: 'pending' | 'uploaded' | 'verified' | 'rejected';
    dueDate?: string;
  }>;
  onUploadClick: (documentId: string) => void;
}

export const DocumentStatusOverview: React.FC<DocumentStatusOverviewProps> = ({
  documents,
  onUploadClick
}) => {
  const pendingDocuments = documents.filter(doc => 
    doc.required && doc.status === 'pending'
  );

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'verified': return COLORS.success.main;
      case 'uploaded': return COLORS.primary;
      case 'rejected': return COLORS.error;
      default: return COLORS.text.secondary;
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h3 style={styles.title}>Outstanding Documents</h3>
        <div style={styles.stats}>
          <span>{pendingDocuments.length} documents pending</span>
          <span>{documents.filter(d => d.status === 'verified').length} verified</span>
        </div>
      </div>

      <div style={styles.documentList}>
        {pendingDocuments.map(doc => (
          <div key={doc.id} style={styles.documentItem}>
            <div style={styles.documentInfo}>
              <h4 style={styles.documentName}>{doc.name}</h4>
              <p style={styles.documentDescription}>{doc.description}</p>
              {doc.dueDate && (
                <span style={styles.dueDate}>Due: {doc.dueDate}</span>
              )}
            </div>
            <button
              onClick={() => onUploadClick(doc.id)}
              style={styles.uploadButton}
            >
              Upload Now
            </button>
          </div>
        ))}
      </div>

      {pendingDocuments.length === 0 && (
        <div style={styles.emptyState}>
          <p>All required documents have been submitted!</p>
        </div>
      )}
    </div>
  );
};

const styles = {
  container: {
    backgroundColor: COLORS.surface,
    borderRadius: '8px',
    padding: SPACING.lg,
    marginBottom: SPACING.xl
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: SPACING.lg
  },
  title: {
    fontSize: TYPOGRAPHY.fontSize.lg,
    fontFamily: TYPOGRAPHY.fontFamily.medium,
    color: COLORS.text.primary,
    margin: 0
  },
  stats: {
    display: 'flex',
    gap: SPACING.md,
    fontSize: TYPOGRAPHY.fontSize.sm,
    color: COLORS.text.secondary
  },
  documentList: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: SPACING.md
  },
  documentItem: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: SPACING.md,
    backgroundColor: COLORS.background,
    borderRadius: '4px',
    border: `1px solid ${COLORS.border}`
  },
  documentInfo: {
    flex: 1
  },
  documentName: {
    fontSize: TYPOGRAPHY.fontSize.md,
    fontFamily: TYPOGRAPHY.fontFamily.medium,
    color: COLORS.text.primary,
    margin: 0,
    marginBottom: SPACING.xs
  },
  documentDescription: {
    fontSize: TYPOGRAPHY.fontSize.sm,
    color: COLORS.text.secondary,
    margin: 0,
    marginBottom: SPACING.xs
  },
  dueDate: {
    fontSize: TYPOGRAPHY.fontSize.xs,
    color: COLORS.error,
    fontFamily: TYPOGRAPHY.fontFamily.medium
  },
  uploadButton: {
    backgroundColor: COLORS.primary,
    color: COLORS.background,
    border: 'none',
    padding: `${SPACING.sm}px ${SPACING.md}px`,
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: TYPOGRAPHY.fontSize.sm,
    fontFamily: TYPOGRAPHY.fontFamily.medium,
    '&:hover': {
      backgroundColor: COLORS.secondary
    }
  },
  emptyState: {
    textAlign: 'center' as const,
    padding: SPACING.xl,
    color: COLORS.text.secondary
  }
};
