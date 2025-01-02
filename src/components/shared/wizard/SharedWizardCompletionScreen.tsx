import React from 'react';
import { COLORS } from '../../../../assets/config/colors';
import { SPACING } from '../../../../assets/config/spacing';
import { TYPOGRAPHY } from '../../../../assets/config/typography';

interface SharedWizardCompletionScreenProps {
  documentCount: number;
  completedDocuments: number;
  onDashboardRedirect: () => void;
  nextSteps?: Array<{
    id: string;
    title: string;
    description: string;
    completed: boolean;
  }>;
}

export const SharedWizardCompletionScreen: React.FC<SharedWizardCompletionScreenProps> = ({
  documentCount,
  completedDocuments,
  onDashboardRedirect,
  nextSteps = []
}) => {
  const progress = (completedDocuments / documentCount) * 100;

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <div style={styles.successIcon}>✓</div>
        <h2 style={styles.title}>Documents Successfully Collected!</h2>
        <p style={styles.subtitle}>
          You've completed the document collection process. Here's what happens next:
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
          {completedDocuments} of {documentCount} documents processed
        </div>
      </div>

      <div style={styles.nextStepsSection}>
        <h3 style={styles.sectionTitle}>Next Steps</h3>
        <div style={styles.stepsList}>
          {nextSteps.map(step => (
            <div key={step.id} style={styles.stepItem}>
              <div style={styles.stepIcon}>
                {step.completed ? '✓' : '→'}
              </div>
              <div style={styles.stepContent}>
                <h4 style={styles.stepTitle}>{step.title}</h4>
                <p style={styles.stepDescription}>{step.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div style={styles.actions}>
        <button
          onClick={onDashboardRedirect}
          style={styles.dashboardButton}
        >
          Go to Dashboard
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
  successIcon: {
    width: '64px',
    height: '64px',
    borderRadius: '50%',
    backgroundColor: COLORS.success.main,
    color: COLORS.background,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '32px',
    margin: '0 auto',
    marginBottom: SPACING.md
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
    backgroundColor: COLORS.success.main,
    transition: 'width 0.3s ease'
  },
  progressText: {
    textAlign: 'center' as const,
    color: COLORS.text.secondary,
    fontSize: TYPOGRAPHY.fontSize.sm
  },
  nextStepsSection: {
    backgroundColor: COLORS.surface,
    borderRadius: '8px',
    padding: SPACING.lg,
    marginBottom: SPACING.xl
  },
  sectionTitle: {
    fontSize: TYPOGRAPHY.fontSize.lg,
    fontFamily: TYPOGRAPHY.fontFamily.medium,
    color: COLORS.text.primary,
    marginBottom: SPACING.md
  },
  stepsList: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: SPACING.md
  },
  stepItem: {
    display: 'flex',
    alignItems: 'flex-start',
    gap: SPACING.md
  },
  stepIcon: {
    width: '24px',
    height: '24px',
    borderRadius: '50%',
    backgroundColor: COLORS.primary,
    color: COLORS.background,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: TYPOGRAPHY.fontSize.sm
  },
  stepContent: {
    flex: 1
  },
  stepTitle: {
    fontSize: TYPOGRAPHY.fontSize.md,
    fontFamily: TYPOGRAPHY.fontFamily.medium,
    color: COLORS.text.primary,
    marginBottom: SPACING.xs
  },
  stepDescription: {
    fontSize: TYPOGRAPHY.fontSize.sm,
    color: COLORS.text.secondary,
    margin: 0
  },
  actions: {
    display: 'flex',
    justifyContent: 'center',
    marginTop: SPACING.xl
  },
  dashboardButton: {
    backgroundColor: COLORS.primary,
    color: COLORS.background,
    border: 'none',
    padding: `${SPACING.md}px ${SPACING.xl}px`,
    borderRadius: '4px',
    fontSize: TYPOGRAPHY.fontSize.md,
    fontFamily: TYPOGRAPHY.fontFamily.medium,
    cursor: 'pointer',
    transition: 'background-color 0.2s ease',
    '&:hover': {
      backgroundColor: COLORS.secondary
    }
  }
};
