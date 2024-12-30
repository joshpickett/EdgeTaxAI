import { COLORS } from '../../../../assets/config/colors';
import { SPACING } from '../../../../assets/config/spacing';
import { TYPOGRAPHY } from '../../../../assets/config/typography';

export const formFieldStyles = {
  container: {
    marginBottom: SPACING.md,
  },

  label: {
    display: 'block',
    marginBottom: SPACING.xs,
    color: COLORS.text.primary,
    fontFamily: TYPOGRAPHY.fontFamily.medium,
    fontSize: TYPOGRAPHY.fontSize.sm,
  },

  input: {
    width: '100%',
    padding: `${SPACING.sm}px ${SPACING.md}px`,
    border: `1px solid ${COLORS.border}`,
    borderRadius: '4px',
    fontSize: TYPOGRAPHY.fontSize.md,
    fontFamily: TYPOGRAPHY.fontFamily.regular,
    color: COLORS.text.primary,
    backgroundColor: COLORS.background,
    transition: 'border-color 0.2s ease',

    '&:focus': {
      outline: 'none',
      borderColor: COLORS.primary,
    },

    '&:disabled': {
      backgroundColor: COLORS.surface,
      color: COLORS.text.disabled,
      cursor: 'not-allowed',
    },
  },

  error: {
    borderColor: COLORS.error,
    '&:focus': {
      borderColor: COLORS.error,
    },
  },

  errorText: {
    color: COLORS.error,
    fontSize: TYPOGRAPHY.fontSize.xs,
    marginTop: SPACING.xs,
    fontFamily: TYPOGRAPHY.fontFamily.regular,
  },

  select: {
    appearance: 'none',
    backgroundImage: 'url("data:image/svg+xml;charset=utf-8,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'12\' height=\'12\' fill=\'none\' stroke=\'%23666\' viewBox=\'0 0 12 12\'%3E%3Cpath d=\'M3 5l3 3 3-3\'/%3E%3C/svg%3E")',
    backgroundRepeat: 'no-repeat',
    backgroundPosition: 'right 12px center',
    paddingRight: SPACING.xl,
  },

  checkbox: {
    container: {
      display: 'flex',
      alignItems: 'center',
      cursor: 'pointer',
    },
    input: {
      width: '20px',
      height: '20px',
      marginRight: SPACING.sm,
    },
  },
};
