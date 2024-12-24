import React from 'react';
import { render, waitFor } from '@testing-library/react-native';
import { useColorScheme } from 'react-native';
import App from '../App';

// Mock the required dependencies
jest.mock('@react-navigation/native', () => ({
  NavigationContainer: ({ children }: { children: React.ReactNode }) => children,
}));

jest.mock('../src/navigation/AppNavigator', () => 'AppNavigator');

jest.mock('../src/store', () => ({
  store: {
    getState: () => ({}),
    dispatch: jest.fn(),
    subscribe: jest.fn(),
  },
}));

jest.mock('react-native/Libraries/Utilities/useColorScheme', () => ({
  __esModule: true,
  default: jest.fn(),
}));

describe('App', () => {
  beforeEach(() => {
    (useColorScheme as jest.Mock).mockReturnValue('light');
  });

  it('renders without crashing', () => {
    const { getByTestId } = render(<App />);
    expect(getByTestId('app-root')).toBeTruthy();
  });

  it('shows loading overlay initially', () => {
    const { getByTestId } = render(<App />);
    expect(getByTestId('loading-overlay')).toBeTruthy();
  });

  it('applies correct theme based on color scheme', () => {
    (useColorScheme as jest.Mock).mockReturnValue('dark');
    const { getByTestId } = render(<App />);
    const rootElement = getByTestId('app-root');
    expect(rootElement.props.style).toContainEqual(
      expect.objectContaining({
        backgroundColor: expect.stringMatching(/#|rgb|rgba/),
      })
    );
  });

  it('hides loading overlay after navigation is ready', async () => {
    const { queryByTestId } = render(<App />);
    await waitFor(() => {
      expect(queryByTestId('loading-overlay')).toBeNull();
    });
  });
});
