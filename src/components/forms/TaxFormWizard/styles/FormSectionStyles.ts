import { COLORS } from '../../../../assets/config/colors';
import { SPACING } from '../../../../assets/config/spacing';
import { TYPOGRAPHY } from '../../../../assets/config/typography';

export const formSectionStyles = {
  container: {
    marginBottom: SPACING.xl,
  },

  header: {
    marginBottom: SPACING.lg,
  },

  title: {
    color: COLORS.text.primary,
    fontSize: TYPOGRAPHY.fontSize.lg,
    fontFamily: TYPOGRAPHY.fontFamily.medium,
    marginBottom: SPACING.xs,
  },

  description: {
    color: COLORS.text.secondary,
    fontSize: TYPOGRAPHY.fontSize.sm,
    fontFamily: TYPOGRAPHY.fontFamily.regular,
  },

  content: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
    gap: SPACING.md,
  },

  footer: {
    marginTop: SPACING.lg,
    paddingTop: SPACING.md,
    borderTop: `1px solid ${COLORS.border}`,
  },

  helpText: {
    backgroundColor: COLORS.surface,
    padding: SPACING.md,
    borderRadius: '4px',
    marginTop: SPACING.md,
    fontSize: TYPOGRAPHY.fontSize.sm,
    color: COLORS.text.secondary,
  },
};
