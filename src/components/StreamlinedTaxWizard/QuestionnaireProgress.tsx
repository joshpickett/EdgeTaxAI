import React from 'react';
import { COLORS } from '../../../assets/config/colors';
import { SPACING } from '../../../assets/config/spacing';
import { TYPOGRAPHY } from '../../../assets/config/typography';

interface QuestionnaireProgressProps {
  currentStep: number;
  totalSteps: number;
  completedSteps: string[];
  sections: Array<{
    id: string;
    title: string;
    isCompleted: boolean;
  }>;
}

export const QuestionnaireProgress: React.FC<QuestionnaireProgressProps> = ({
  currentStep,
  totalSteps,
  completedSteps,
  sections
}) => {
  const progress = (completedSteps.length / totalSteps) * 100;

  return (
    <div style={styles.container}>
      <div style={styles.progressBar}>
        <div 
          style={{
            ...styles.progressFill,
            width: `${progress}%`
          }}
        />
      </div>
      <div style={styles.stepIndicator}>
        <span style={styles.currentStep}>
          Step {currentStep + 1}
        </span>
        <span style={styles.totalSteps}>
          of {totalSteps}
        </span>
        <div style={styles.sectionProgress}>
          {sections.map(section => (
            <div 
              key={section.id}
              style={{
                ...styles.sectionItem,
                ...(section.isCompleted ? styles.completedSection : {})
              }}
            >
              {section.title}
            </div>
          ))}
        </div>
      </div>
      {completedSteps.length > 0 && (
        <div style={styles.completionStatus}>
          {completedSteps.length} of {totalSteps} questions completed
        </div>
      )}
    </div>
  );
};

const styles = {
  container: {
    padding: SPACING.md,
    marginBottom: SPACING.lg
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
  stepIndicator: {
    display: 'flex',
    justifyContent: 'center',
    gap: SPACING.xs,
    marginBottom: SPACING.sm
  },
  currentStep: {
    fontSize: TYPOGRAPHY.fontSize.md,
    fontFamily: TYPOGRAPHY.fontFamily.medium,
    color: COLORS.text.primary
  },
  totalSteps: {
    fontSize: TYPOGRAPHY.fontSize.md,
    fontFamily: TYPOGRAPHY.fontFamily.regular,
    color: COLORS.text.secondary
  },
  completionStatus: {
    fontSize: TYPOGRAPHY.fontSize.sm,
    color: COLORS.text.secondary,
    textAlign: 'center' as const
  },
  sectionProgress: {
    display: 'flex',
    gap: SPACING.md,
    marginTop: SPACING.md
  },
  sectionItem: {
    padding: SPACING.sm,
    borderRadius: '4px',
    backgroundColor: COLORS.surface,
    fontSize: TYPOGRAPHY.fontSize.sm,
    color: COLORS.text.secondary
  },
  completedSection: {
    backgroundColor: COLORS.primary,
    color: COLORS.background
  }
};
