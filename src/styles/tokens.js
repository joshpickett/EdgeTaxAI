// Design System Tokens

// Brand Identity
export const brand = {
  name: 'EdgeTaxAI',
  version: '1.0.0',
  description: 'Smart Tax Solutions for Gig Economy Workers',
  author: 'EdgeTaxAI Team'
};

// Device-specific typography
export const deviceTypography = {
  ios: {
    heading: 'SF Pro Display',
    body: 'SF Pro Text',
    code: 'SF Mono'
  },
  android: {
    heading: 'Roboto',
    body: 'Roboto',
    code: 'Roboto Mono'
  }
};

export const colors = {
  // Brand Colors
  primary: {
    50: '#E3F2FD',
    100: '#BBDEFB',
    200: '#90CAF9',
    300: '#64B5F6',
    400: '#42A5F5',
    main: '#007AFF',
    500: '#2196F3',
    600: '#1E88E5',
    700: '#1976D2',
    800: '#1565C0',
    900: '#0D47A1',
    light: '#47A1FF',
    dark: '#0056B3',
    contrast: '#FFFFFF'
  },
  secondary: {
    main: '#4ECDC4',
    light: '#7EDAD4',
    dark: '#36908A',
    contrast: '#000000'
  },
  error: {
    main: '#FF6B6B',
    light: '#FF9B9B',
    dark: '#CC5555',
    contrast: '#FFFFFF'
  },
  warning: {
    main: '#FFD93D',
    light: '#FFE584',
    dark: '#B39628',
    contrast: '#000000'
  },
  success: {
    main: '#6BCB77',
    light: '#95DC9E',
    dark: '#4B8F53',
    contrast: '#FFFFFF'
  },
  grey: {
    50: '#FAFAFA',
    100: '#F5F5F5',
    200: '#EEEEEE',
    300: '#E0E0E0',
    400: '#BDBDBD',
    500: '#9E9E9E',
    600: '#757575',
    700: '#616161',
    800: '#424242',
    900: '#212121'
  },
  text: {
    primary: '#212121',
    secondary: '#757575',
    disabled: '#9E9E9E'
  },

  // Dark mode color palette
  darkMode: {
    primary: {
      main: '#60A5FA',  // Lighter blue for dark mode
      light: '#93C5FD',
      dark: '#2563EB',
      contrast: '#000000'
    },
    background: {
      default: '#121212',
      paper: '#1E1E1E',
      elevated: '#242424'
    },
    text: {
      primary: '#FFFFFF',
      secondary: '#B0B0B0',
      disabled: '#666666'
    },
    divider: 'rgba(255, 255, 255, 0.12)',
    action: {
      active: '#FFFFFF',
      hover: 'rgba(255, 255, 255, 0.08)',
      selected: 'rgba(255, 255, 255, 0.16)',
      disabled: 'rgba(255, 255, 255, 0.3)'
    }
  }
};

// Typography
export const typography = {
  fontFamily: {
    primary: 'Inter',
    secondary: 'Roboto',
    monospace: 'Roboto Mono',
    heading: 'Inter',
    body: 'Roboto'
  },
  fontSize: {
    xs: 12,
    sm: 14,
    md: 16,
    lg: 18,
    xl: 20,
    '2xl': 24,
    '3xl': 30,
    '4xl': 36
  },
  
  // Mobile-specific adjustments
  mobile: {
    fontSize: {
      xs: 11,
      sm: 13,
      md: 15,
      lg: 17,
      xl: 19
    }
  },

  fontWeight: {
    light: '300',
    regular: '400',
    medium: '500',
    semibold: '600',
    bold: '700'
  },
  lineHeight: {
    tight: 1.2,
    normal: 1.5,
    relaxed: 1.75
  },
  letterSpacing: {
    tight: -0.5,
    normal: 0,
    wide: 0.5
  }
};

// Spacing
export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  '2xl': 48,
  '3xl': 64
};

// Border Radius
export const borderRadius = {
  none: 0,
  sm: 4,
  md: 8,
  lg: 12,
  xl: 16,
  full: 9999
};

// Shadows
export const shadows = {
  none: 'none',
  sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  md: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
  lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
  xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1)'
};

// Breakpoints
export const breakpoints = {
  xs: 0,
  sm: 600,
  md: 960,
  lg: 1280,
  xl: 1920
};

// Responsive breakpoints
breakpoints: {
  xs: 0,    // phones
  sm: 600,  // tablets
  md: 960,  // small laptops
  lg: 1280, // desktops
  xl: 1920  // large screens
},

// Device-specific adjustments
deviceSpecific: {
  ios: {
    spacing: { base: 8, scale: 1.2 },
    typography: { scale: 1.1 }
  },
  android: {
    spacing: { base: 8, scale: 1 },
    typography: { scale: 1 }
  }
},

// Animation and Transition tokens
animation: {
  duration: {
    fast: '150ms',
    normal: '300ms',
    slow: '450ms'
  },
  easing: {
    easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
    easeOut: 'cubic-bezier(0, 0, 0.2, 1)',
    easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)'
  }
},

// Elevation/Shadow tokens
elevation: {
  none: 'none',
  sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  md: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
  lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
  xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1)'
},

// Z-index scale
zIndex: {
  modal: 1000,
  overlay: 900,
  drawer: 800,
  popover: 700,
  header: 600,
  dropdown: 500
};
