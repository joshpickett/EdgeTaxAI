import { COLORS } from '../../../../assets/config/colors';
import { SPACING } from '../../../../assets/config/spacing';
import { TYPOGRAPHY } from '../../../../assets/config/typography';

export const wizardStyles = {
  container: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: `${SPACING.lg}px`,
    backgroundColor: COLORS.background,
  },

  progressBar: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: `${SPACING.xl}px`,
  },

  step: {
    display: 'flex',
    alignItems: 'center',
    flex: 1,
  },

  stepNumber: {
    width: '32px',
    height: '32px',
    borderRadius: '50%',
    backgroundColor: COLORS.primary,
    color: COLORS.background,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: `${SPACING.sm}px`,
    fontFamily: TYPOGRAPHY.fontFamily.medium,
    fontSize: TYPOGRAPHY.fontSize.md,
  },

  stepTitle: {
    color: COLORS.text.primary,
    fontFamily: TYPOGRAPHY.fontFamily.regular,
    fontSize: TYPOGRAPHY.fontSize.md,
  },

  stepConnector: {
    flex: 1,
    height: '2px',
    backgroundColor: COLORS.border,
    margin: `0 ${SPACING.md}px`,
  },

  content: {
    backgroundColor: COLORS.surface,
    padding: `${SPACING.xl}px`,
    borderRadius: '8px',
    marginBottom: `${SPACING.xl}px`,
  },

  navigation: {
    display: 'flex',
    justifyContent: 'space-between',
    padding: `${SPACING.lg}px 0`,
  },

  button: {
    base: {
      padding: `${SPACING.sm}px ${SPACING.lg}px`,
      borderRadius: '4px',
      fontFamily: TYPOGRAPHY.fontFamily.medium,
      fontSize: TYPOGRAPHY.fontSize.md,
      cursor: 'pointer',
      transition: 'all 0.2s ease',
    },
    primary: {
      backgroundColor: COLORS.primary,
      color: COLORS.background,
      border: 'none',
      '&:hover': {
        backgroundColor: COLORS.secondary,
      },
      '&:disabled': {
        backgroundColor: COLORS.text.disabled,
        cursor: 'not-allowed',
      },
    },
    secondary: {
      backgroundColor: COLORS.background,
      color: COLORS.primary,
      border: `1px solid ${COLORS.primary}`,
      '&:hover': {
        backgroundColor: COLORS.surface,
      },
      '&:disabled': {
        borderColor: COLORS.text.disabled,
        color: COLORS.text.disabled,
        cursor: 'not-allowed',
      },
    },
  },
};
