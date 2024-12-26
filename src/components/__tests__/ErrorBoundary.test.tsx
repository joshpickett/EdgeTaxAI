import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import ErrorBoundary from '../ErrorBoundary';
import { Text } from 'react-native';

describe('ErrorBoundary', () => {
  const ThrowError = () => {
    throw new Error('Test error');
  };

  it('renders children when no error occurs', () => {
    const { getByText } = render(
      <ErrorBoundary>
        <Text>Test Content</Text>
      </ErrorBoundary>
    );
    expect(getByText('Test Content')).toBeTruthy();
  });

  it('renders error UI when error occurs', () => {
    const { getByText } = render(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    );
    
    expect(getByText('Oops! Something went wrong')).toBeTruthy();
    expect(getByText('Test error')).toBeTruthy();
  });

  it('allows retry after error', () => {
    const { getByText, queryByText } = render(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    );
    
    fireEvent.press(getByText('Try Again'));
    expect(queryByText('Oops! Something went wrong')).toBeTruthy();
  });
});
