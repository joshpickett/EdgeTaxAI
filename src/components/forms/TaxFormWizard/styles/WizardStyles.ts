import { COLORS } from '../../../../assets/config/colors';
import { SPACING } from '../../../../assets/config/spacing';
import { TYPOGRAPHY } from '../../../../assets/config/typography';

export const wizardStyles = {
  container: {
    width: '100%',
    maxWidth: '960px',
    margin: '0 auto',
    padding: SPACING.lg
  },
  
  progressBar: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: SPACING.xl,
    position: 'relative' as const
  },
  
  step: {
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'center',
    position: 'relative' as const,
    flex: 1
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
    fontFamily: TYPOGRAPHY.fontFamily.medium,
    fontSize: TYPOGRAPHY.fontSize.md,
    marginBottom: SPACING.xs
  },
  
  stepTitle: {
    fontSize: TYPOGRAPHY.fontSize.sm,
    color: COLORS.text.secondary,
    textAlign: 'center' as const
  },
  
  stepConnector: {
    position: 'absolute' as const,
    top: '16px',
    left: '50%',
    right: '-50%',
    height: '2px',
    backgroundColor: COLORS.border
  },
  
  content: {
    backgroundColor: COLORS.background,
    borderRadius: '8px',
    padding: SPACING.xl,
    marginBottom: SPACING.xl,
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
  },
  
  navigation: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: SPACING.md
  },
  
  button: {
    base: {
      padding: `${SPACING.sm}px ${SPACING.md}px`,
      borderRadius: '4px',
      fontSize: TYPOGRAPHY.fontSize.md,
      fontFamily: TYPOGRAPHY.fontFamily.medium,
      cursor: 'pointer',
      border: 'none',
      transition: 'all 0.2s ease'
    },
    primary: {
      backgroundColor: COLORS.primary,
      color: COLORS.background,
      '&:hover': {
        backgroundColor: COLORS.secondary
      },
      '&:disabled': {
        backgroundColor: COLORS.text.disabled,
        cursor: 'not-allowed'
      }
    },
    secondary: {
      backgroundColor: COLORS.surface,
      color: COLORS.text.primary,
      border: `1px solid ${COLORS.border}`,
      '&:hover': {
        backgroundColor: COLORS.divider
      },
      '&:disabled': {
        color: COLORS.text.disabled,
        cursor: 'not-allowed'
      }
    }
  }
};
