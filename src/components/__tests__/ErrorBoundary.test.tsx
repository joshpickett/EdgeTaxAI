import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import { setupSrcPath } from '../../setup_path';
import ErrorBoundary from '../ErrorBoundary';
import { Text } from 'react-native';
import { colors, typography } from '../../styles/tokens';

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
    
    const errorTitle = getByText('Oops! Something went wrong');
    expect(errorTitle.props.style).toContainEqual(
      expect.objectContaining({ fontSize: typography.fontSize.xl })
    );
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
