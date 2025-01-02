import React, { useState } from 'react';
import { COLORS } from '../../../../assets/config/colors';
import { SPACING } from '../../../../assets/config/spacing';
import { TYPOGRAPHY } from '../../../../assets/config/typography';
import { DocumentType } from '../../../types/documents';

interface SharedWizardDocumentRequirementsScreenProps {
  requiredDocuments: Array<{
    id: string;
    type: DocumentType;
    name: string;
    description: string;
    required: boolean;
    category?: string;
    priority?: 'high' | 'medium' | 'low';
    deadline?: string;
    status?: 'pending' | 'uploaded' | 'verified' | 'rejected';
  }>;
  onContinue: () => void;
  onBack: () => void;
  onDocumentSelect?: (documentId: string) => void;
}

const DocumentRequirementCard = ({ document, onSelect }) => {
  // New component implementation for document cards
  return (
    <div style={styles.documentCard}>
      {/* Document card content */}
    </div>
  );
};

export const SharedWizardDocumentRequirementsScreen: React.FC<SharedWizardDocumentRequirementsScreenProps> = ({
  requiredDocuments,
  onContinue,
  onBack
}) => {
  const [expandedDocument, setExpandedDocument] = useState<string | null>(null);

  const requiredCount = requiredDocuments.filter(doc => doc.required).length;
  const uploadedCount = requiredDocuments.filter(doc => doc.status === 'uploaded' || doc.status === 'verified').length;

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h2 style={styles.title}>Document Requirements</h2>
        <p style={styles.subtitle}>
          We've analyzed your tax situation and identified the following required documents
        </p>
        <div style={styles.summaryStats}>
          <div style={styles.stat}>
            <span style={styles.statNumber}>{requiredDocuments.length}</span>
            <span style={styles.statLabel}>Total Documents</span>
          </div>
          <div style={styles.stat}>
            <span style={styles.statNumber}>
              {requiredDocuments.filter(d => d.required).length}
            </span>
            <span style={styles.statLabel}>Required</span>
          </div>
          <div style={styles.stat}>
            <span style={styles.statNumber}>
              {requiredDocuments.filter(d => d.status === 'verified').length}
            </span>
            <span style={styles.statLabel}>Completed</span>
          </div>
        </div>
      </div>

      <div style={styles.progress}>
        <div style={styles.progressText}>
          {uploadedCount} of {requiredCount} required documents ready
        </div>
        <div style={styles.progressBar}>
          <div 
            style={{
              ...styles.progressFill,
              width: `${(uploadedCount / requiredCount) * 100}%`
            }}
          />
        </div>
      </div>

      <div style={styles.documentList}>
        {requiredDocuments.map(doc => (
          <div 
            key={doc.id}
            style={styles.documentCard}
            onClick={() => setExpandedDocument(expandedDocument === doc.id ? null : doc.id)}
          >
            <div style={styles.documentHeader}>
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

            {expandedDocument === doc.id && (
              <div style={styles.documentDetails}>
                <p style={styles.documentDescription}>{doc.description}</p>
              </div>
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
          onClick={onContinue}
          style={styles.continueButton}
          disabled={uploadedCount < requiredCount}
        >
          Continue to Upload
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
  progress: {
    marginBottom: SPACING.xl
  },
  progressText: {
    fontSize: TYPOGRAPHY.fontSize.sm,
    color: COLORS.text.secondary,
    marginBottom: SPACING.xs
  },
  progressBar: {
    height: '4px',
    backgroundColor: COLORS.surface,
    borderRadius: '2px'
  },
  progressFill: {
    height: '100%',
    backgroundColor: COLORS.primary,
    borderRadius: '2px',
    transition: 'width 0.3s ease'
  },
  documentList: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: SPACING.md
  },
  documentCard: {
    backgroundColor: COLORS.surface,
    borderRadius: '8px',
    padding: SPACING.md,
    cursor: 'pointer',
    transition: 'box-shadow 0.2s ease',
    '&:hover': {
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
    }
  },
  documentHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center'
  },
  documentInfo: {
    display: 'flex',
    alignItems: 'center',
    gap: SPACING.sm
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
  documentDetails: {
    marginTop: SPACING.md,
    paddingTop: SPACING.md,
    borderTop: `1px solid ${COLORS.border}`
  },
  documentDescription: {
    fontSize: TYPOGRAPHY.fontSize.sm,
    color: COLORS.text.secondary,
    margin: 0
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
  },
  summaryStats: {
    display: 'flex',
    justifyContent: 'space-around',
    marginTop: SPACING.lg,
    padding: SPACING.md,
    backgroundColor: COLORS.surface,
    borderRadius: '8px'
  },
  stat: {
    textAlign: 'center',
    padding: SPACING.md
  },
  statNumber: {
    display: 'block',
    fontSize: TYPOGRAPHY.fontSize.xl,
    fontWeight: 'bold',
    color: COLORS.primary
  },
  statLabel: {
    fontSize: TYPOGRAPHY.fontSize.sm,
    color: COLORS.text.secondary
  },
  categorySection: {
    marginTop: SPACING.xl
  },
  categoryTitle: {
    fontSize: TYPOGRAPHY.fontSize.lg,
    fontWeight: 'bold',
    marginBottom: SPACING.md
  },
  documentsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
    gap: SPACING.md
  },
  priorityBadge: {
    padding: `${SPACING.xs}px ${SPACING.sm}px`,
    borderRadius: '4px',
    fontSize: TYPOGRAPHY.fontSize.xs,
    fontWeight: 'bold'
  }
};
