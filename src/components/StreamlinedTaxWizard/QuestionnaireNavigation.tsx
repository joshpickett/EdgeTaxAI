import React from 'react';
import { COLORS } from '../../../assets/config/colors';
import { SPACING } from '../../../assets/config/spacing';
import { TYPOGRAPHY } from '../../../assets/config/typography';

interface QuestionnaireNavigationProps {
  canGoBack: boolean;
  canGoForward: boolean;
  onBack: () => void;
  onNext: () => void;
  onSave?: () => void;
  isLastStep: boolean;
  isSaving?: boolean;
}

export const QuestionnaireNavigation: React.FC<QuestionnaireNavigationProps> = ({
  canGoBack,
  canGoForward,
  onBack,
  onNext,
  onSave,
  isLastStep,
  isSaving = false
}) => {
  return (
    <div style={styles.container}>
      <button
        style={{
          ...styles.button,
          ...styles.backButton,
          ...(canGoBack ? {} : styles.disabledButton)
        }}
        onClick={onBack}
        disabled={!canGoBack}
      >
        Previous
      </button>

      <div style={styles.rightButtons}>
        {onSave && (
          <button
            style={{
              ...styles.button,
              ...styles.saveButton,
              ...(isSaving ? styles.disabledButton : {})
            }}
            onClick={onSave}
            disabled={isSaving}
          >
            {isSaving ? 'Saving...' : 'Save Progress'}
          </button>
        )}

        <button
          style={{
            ...styles.button,
            ...styles.nextButton,
            ...(canGoForward ? {} : styles.disabledButton)
          }}
          onClick={onNext}
          disabled={!canGoForward}
        >
          {isLastStep ? 'Complete' : 'Next'}
        </button>
      </div>
    </div>
  );
};

const styles = {
  container: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: SPACING.md,
    borderTop: `1px solid ${COLORS.border}`,
    marginTop: SPACING.lg
  },
  rightButtons: {
    display: 'flex',
    gap: SPACING.md
  },
  button: {
    padding: `${SPACING.sm}px ${SPACING.md}px`,
    borderRadius: '4px',
    fontSize: TYPOGRAPHY.fontSize.md,
    fontFamily: TYPOGRAPHY.fontFamily.medium,
    cursor: 'pointer',
    border: 'none',
    transition: 'all 0.2s ease'
  },
  backButton: {
    backgroundColor: COLORS.surface,
    color: COLORS.text.primary,
    border: `1px solid ${COLORS.border}`
  },
  nextButton: {
    backgroundColor: COLORS.primary,
    color: COLORS.background
  },
  saveButton: {
    backgroundColor: COLORS.surface,
    color: COLORS.text.primary,
    border: `1px solid ${COLORS.border}`
  },
  disabledButton: {
    opacity: 0.5,
    cursor: 'not-allowed'
  }
};
