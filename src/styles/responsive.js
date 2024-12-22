import { Dimensions } from 'react-native';
import { breakpoints } from './tokens';

const window = Dimensions.get('window');

export const getResponsiveValue = (values) => {
  const width = window.width;

  if (width >= breakpoints.xl) return values.xl || values.lg || values.md || values.sm || values.xs;
  if (width >= breakpoints.lg) return values.lg || values.md || values.sm || values.xs;
  if (width >= breakpoints.md) return values.md || values.sm || values.xs;
  if (width >= breakpoints.sm) return values.sm || values.xs;
  return values.xs;
};

export const isSmallScreen = () => window.width < breakpoints.sm;
export const isMediumScreen = () => window.width >= breakpoints.sm && window.width < breakpoints.md;
export const isLargeScreen = () => window.width >= breakpoints.md;

export const responsiveSize = (size) => {
  const baseWidth = 375; // iPhone SE width
  const scale = window.width / baseWidth;
  return Math.round(size * scale);
};
