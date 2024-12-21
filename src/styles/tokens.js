// Color Palette
export const colors = {
  primary: {
    main: '#007BFF',
    light: '#4DA3FF',
    dark: '#0056B3',
    contrast: '#FFFFFF'
  },
  secondary: {
    main: '#6C757D',
    light: '#A1A9B0',
    dark: '#494F54',
    contrast: '#FFFFFF'
  },
  success: {
    main: '#28A745',
    light: '#48D368',
    dark: '#1E7E34',
    contrast: '#FFFFFF'
  },
  error: {
    main: '#DC3545',
    light: '#E4606D',
    dark: '#BD2130',
    contrast: '#FFFFFF'
  },
  warning: {
    main: '#FFC107',
    light: '#FFCD39',
    dark: '#D39E00',
    contrast: '#000000'
  },
  grey: {
    300: '#D1D1D1'
  }
};

// Typography
export const typography = {
  fontFamily: {
    primary: 'Roboto, sans-serif',
    secondary: 'Arial, sans-serif'
  },
  fontSize: {
    xs: '0.75rem',    // 12px
    sm: '0.875rem',   // 14px
    base: '1rem',     // 16px
    lg: '1.125rem',   // 18px
    xl: '1.25rem',    // 20px
    '2xl': '1.5rem',  // 24px
    '3xl': '1.875rem' // 30px
  },
  fontWeight: {
    light: 300,
    regular: 400,
    medium: 500,
    bold: 700
  }
};

// Spacing
export const spacing = {
  xs: '0.25rem',   // 4px
  sm: '0.5rem',    // 8px
  md: '1rem',      // 16px
  lg: '1.5rem',    // 24px
  xl: '2rem',      // 32px
  '2xl': '2.5rem', // 40px
  '3xl': '3rem'    // 48px
};

// Animation
export const animation = {
  duration: {
    fast: '150ms',
    normal: '300ms',
    slow: '500ms'
  },
  easing: {
    easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
    easeOut: 'cubic-bezier(0.0, 0, 0.2, 1)',
    easeIn: 'cubic-bezier(0.4, 0, 1, 1)'
  }
};
