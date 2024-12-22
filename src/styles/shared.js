import { StyleSheet } from 'react-native';
import { colors, typography, spacing, borderRadius, shadows } from './tokens';

export const sharedStyles = StyleSheet.create({
  // Screen Containers
  safeArea: {
    flex: 1,
    backgroundColor: colors.grey[50]
  },
  screenContainer: {
    flex: 1,
    padding: spacing.md
  },
  scrollContainer: {
    flexGrow: 1
  },

  // Layout
  container: {
    flex: 1,
    backgroundColor: colors.grey[50]
  },
  contentContainer: {
    padding: spacing.md,
    backgroundColor: colors.grey[50]
  },
  section: {
    marginBottom: spacing.xl
  },

  // Cards
  card: {
    backgroundColor: colors.grey[50],
    borderRadius: borderRadius.md,
    padding: spacing.md,
    marginVertical: spacing.sm,
    ...shadows.md
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.sm
  },
  cardTitle: {
    fontSize: typography.fontSize.lg,
    fontWeight: typography.fontWeight.semibold,
    color: colors.text.primary
  },

  // Text Styles
  heading1: {
    fontSize: typography.fontSize['3xl'],
    fontFamily: typography.fontFamily.heading,
    fontWeight: typography.fontWeight.bold,
    letterSpacing: typography.letterSpacing.tight,
    color: colors.text.primary,
    marginBottom: spacing.md
  },
  heading2: {
    fontSize: typography.fontSize['2xl'],
    fontWeight: typography.fontWeight.semibold,
    color: colors.text.primary,
    marginBottom: spacing.sm
  },
  bodyText: {
    fontSize: typography.fontSize.md,
    color: colors.text.primary,
    lineHeight: typography.lineHeight.normal
  },
  caption: {
    fontSize: typography.fontSize.sm,
    color: colors.text.secondary
  },

  // Buttons
  button: {
    backgroundColor: colors.primary.main,
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    borderRadius: borderRadius.md,
    alignItems: 'center',
    justifyContent: 'center'
  },
  buttonPrimary: {
    backgroundColor: colors.primary.main,
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    borderRadius: borderRadius.md
  },
  buttonSecondary: {
    backgroundColor: colors.secondary.main,
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    borderRadius: borderRadius.md
  },
  buttonDisabled: {
    backgroundColor: colors.grey[300],
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    borderRadius: borderRadius.md
  },
  buttonLoading: {
    opacity: 0.7
  },
  buttonText: {
    color: colors.primary.contrast,
    fontSize: typography.fontSize.md,
    fontWeight: typography.fontWeight.medium
  },
  buttonOutline: {
    backgroundColor: 'transparent',
    borderWidth: 1,
    borderColor: colors.primary.main
  },
  buttonOutlineText: {
    color: colors.primary.main
  },

  // Forms
  input: {
    backgroundColor: colors.grey[100],
    borderRadius: borderRadius.md,
    padding: spacing.md,
    fontSize: typography.fontSize.md,
    color: colors.text.primary,
    borderWidth: 1,
    borderColor: colors.grey[300]
  },
  inputLabel: {
    fontSize: typography.fontSize.sm,
    color: colors.text.secondary,
    marginBottom: spacing.xs
  },
  inputError: {
    borderColor: colors.error.main
  },
  errorText: {
    color: colors.error.main,
    fontSize: typography.fontSize.sm,
    marginTop: spacing.xs
  },

  // Lists
  list: {
    paddingVertical: spacing.sm
  },
  listItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: colors.grey[200]
  },

  // Spacing
  mt1: { marginTop: spacing.sm },
  mt2: { marginTop: spacing.md },
  mt3: { marginTop: spacing.lg },
  mb1: { marginBottom: spacing.sm },
  mb2: { marginBottom: spacing.md },
  mb3: { marginBottom: spacing.lg },
  mx1: { marginHorizontal: spacing.sm },
  mx2: { marginHorizontal: spacing.md },
  mx3: { marginHorizontal: spacing.lg },
  my1: { marginVertical: spacing.sm },
  my2: { marginVertical: spacing.md },
  my3: { marginVertical: spacing.lg },

  // Padding
  p1: { padding: spacing.sm },
  p2: { padding: spacing.md },
  p3: { padding: spacing.lg },
  px1: { paddingHorizontal: spacing.sm },
  px2: { paddingHorizontal: spacing.md },
  px3: { paddingHorizontal: spacing.lg },
  py1: { paddingVertical: spacing.sm },
  py2: { paddingVertical: spacing.md },
  py3: { paddingVertical: spacing.lg },

  // Platform-specific styles
  platformStyles: {
    ios: {
      button: {
        borderRadius: 8,
        shadowColor: colors.grey[900],
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.25,
        shadowRadius: 4
      },
      input: {
        borderRadius: 10,
        borderWidth: 1,
        padding: spacing.md
      }
    },
    android: {
      button: {
        borderRadius: 4,
        elevation: 4,
        overflow: 'hidden'
      },
      input: {
        borderRadius: 4,
        borderWidth: 0,
        elevation: 2,
        padding: spacing.lg
      }
    }
  }
});
