import React from 'react';
import { COLORS } from '../../../../assets/config/colors';
import { SPACING } from '../../../../assets/config/spacing';
import { TYPOGRAPHY } from '../../../../assets/config/typography';
import { DocumentStatusOverview } from './DocumentStatusOverview';

interface SharedWizardLandingScreenProps {
  onStart: () => void;
  documents: Array<any>;
  onDocumentUpload: (documentId: string) => void;
  documentCount?: number;
  completedDocuments?: number;
}

export const SharedWizardLandingScreen: React.FC<SharedWizardLandingScreenProps> = ({
  onStart,
  documents,
  onDocumentUpload,
  documentCount = 0,
  completedDocuments = 0
}) => {
  const progress = documentCount > 0 ? (completedDocuments / documentCount) * 100 : 0;

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.title}>Document Collection Wizard</h1>
        <p style={styles.subtitle}>
          Let's gather the documents needed for your tax return
        </p>
      </div>

      <div style={styles.progressSection}>
        <div style={styles.progressBar}>
          <div 
            style={{
              ...styles.progressFill,
              width: `${progress}%`
            }}
          />
        </div>
        <div style={styles.progressText}>
          {completedDocuments} of {documentCount} documents collected
        </div>
      </div>

      <div style={styles.content}>
        {documents.length > 0 && (
          <DocumentStatusOverview
            documents={documents}
            onUploadClick={onDocumentUpload}
          />
        )}

        <div style={styles.infoCard}>
          <h3 style={styles.infoTitle}>What to Expect</h3>
          <ul style={styles.infoList}>
            <li>Answer a few questions about your tax situation</li>
            <li>Get a personalized list of required documents</li>
            <li>Upload or import your documents</li>
            <li>Review and verify document information</li>
          </ul>
        </div>

        <button 
          onClick={onStart}
          style={styles.startButton}
        >
          Start Document Collection
        </button>
      </div>
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
    textAlign: 'center' as const,
    marginBottom: SPACING.xl
  },
  title: {
    fontSize: TYPOGRAPHY.fontSize.xxl,
    fontFamily: TYPOGRAPHY.fontFamily.bold,
    color: COLORS.text.primary,
    marginBottom: SPACING.sm
  },
  subtitle: {
    fontSize: TYPOGRAPHY.fontSize.lg,
    color: COLORS.text.secondary,
    fontFamily: TYPOGRAPHY.fontFamily.regular
  },
  progressSection: {
    marginBottom: SPACING.xl
  },
  progressBar: {
    height: '8px',
    backgroundColor: COLORS.surface,
    borderRadius: '4px',
    overflow: 'hidden',
    marginBottom: SPACING.sm
  },
  progressFill: {
    height: '100%',
    backgroundColor: COLORS.primary,
    transition: 'width 0.3s ease'
  },
  progressText: {
    textAlign: 'center' as const,
    color: COLORS.text.secondary,
    fontSize: TYPOGRAPHY.fontSize.sm
  },
  content: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: SPACING.xl,
    alignItems: 'center'
  },
  infoCard: {
    backgroundColor: COLORS.surface,
    padding: SPACING.lg,
    borderRadius: '8px',
    width: '100%'
  },
  infoTitle: {
    fontSize: TYPOGRAPHY.fontSize.lg,
    fontFamily: TYPOGRAPHY.fontFamily.medium,
    color: COLORS.text.primary,
    marginBottom: SPACING.md
  },
  infoList: {
    listStyle: 'none',
    padding: 0,
    margin: 0,
    '& li': {
      marginBottom: SPACING.sm,
      paddingLeft: SPACING.md,
      position: 'relative',
      '&:before': {
        content: '"•"',
        position: 'absolute',
        left: 0,
        color: COLORS.primary
      }
    }
  },
  startButton: {
    backgroundColor: COLORS.primary,
    color: COLORS.background,
    padding: `${SPACING.md}px ${SPACING.xl}px`,
    borderRadius: '4px',
    border: 'none',
    fontSize: TYPOGRAPHY.fontSize.md,
    fontFamily: TYPOGRAPHY.fontFamily.medium,
    cursor: 'pointer',
    transition: 'background-color 0.2s ease',
    '&:hover': {
      backgroundColor: COLORS.secondary
    }
  }
};
