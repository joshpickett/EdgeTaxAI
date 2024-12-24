import React from 'react';
import { render } from '@testing-library/react-native';
import { Provider } from 'react-redux';
import { store } from '../store';
import App from '../../App';
import AppNavigator from '../navigation/AppNavigator';

// Mock dependencies
jest.mock('../navigation/AppNavigator', () => {
  return jest.fn().mockImplementation(() => null);
});

describe('App', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
  });

  it('should render without crashing', () => {
    render(<App />);
    expect(AppNavigator).toHaveBeenCalled();
  });

  it('should provide Redux store to components', () => {
    const { UNSAFE_root } = render(<App />);
    const provider = UNSAFE_root.findByType(Provider);
    
    expect(provider.props.store).toBe(store);
  });

  describe('Redux Integration', () => {
    it('should pass store to Provider', () => {
      const { UNSAFE_root } = render(<App />);
      const provider = UNSAFE_root.findByType(Provider);
      
      expect(provider.props.store.getState()).toBeDefined();
    });
  });

  describe('Navigation Integration', () => {
    it('should render AppNavigator', () => {
      render(<App />);
      expect(AppNavigator).toHaveBeenCalledTimes(1);
    });
  });

  describe('Error Boundary', () => {
    beforeEach(() => {
      // Mock console.error to prevent error logging during tests
      console.error = jest.fn();
    });

    it('should handle render errors gracefully', () => {
      AppNavigator.mockImplementationOnce(() => {
        throw new Error('Test error');
      });

      expect(() => render(<App />)).not.toThrow();
    });
  });
});
