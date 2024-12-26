import '@testing-library/jest-dom';
import 'jest-environment-jsdom';

// Mock Redux store
jest.mock('./store', () => ({
  store: {
    getState: () => ({}),
    dispatch: jest.fn(),
    subscribe: jest.fn(),
  },
}));

// Setup global mocks
global.console = {
  ...console,
  // Silence console.error in tests
  error: jest.fn(),
  // Silence console.warn in tests
  warn: jest.fn(),
};

// Mock react-native-safe-area-context
jest.mock('react-native-safe-area-context', () => ({
  SafeAreaProvider: ({ children }) => children,
  SafeAreaView: ({ children }) => children,
  useSafeAreaInsets: () => ({ top: 0, right: 0, bottom: 0, left: 0 }),
}));
