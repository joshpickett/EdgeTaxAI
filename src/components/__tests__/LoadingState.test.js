import React from 'react';
import { render } from '@testing-library/react-native';
import LoadingState from '../LoadingState';

describe('LoadingState', () => {
  it('renders loading spinner', () => {
    const { getByTestId } = render(<LoadingState />);
    expect(getByTestId('loading-spinner')).toBeTruthy();
  });

  it('renders with custom message', () => {
    const message = 'Custom loading message';
    const { getByText } = render(<LoadingState message={message} />);
    expect(getByText(message)).toBeTruthy();
  });

  it('renders with default message when none provided', () => {
    const { getByText } = render(<LoadingState />);
    expect(getByText('Loading...')).toBeTruthy();
  });

  it('applies custom styles', () => {
    const customStyle = { backgroundColor: 'red' };
    const { getByTestId } = render(<LoadingState style={customStyle} />);
    const container = getByTestId('loading-container');
    expect(container.props.style).toContainEqual(customStyle);
  });
});
