import React from 'react';
import { render } from '@testing-library/react-native';
import LoadingOverlay from '../LoadingOverlay';

describe('LoadingOverlay', () => {
  it('renders correctly when visible', () => {
    const { getByTestId } = render(<LoadingOverlay visible={true} />);
    expect(getByTestId('loading-overlay')).toBeTruthy();
    expect(getByTestId('loading-spinner')).toBeTruthy();
  });

  it('does not render when not visible', () => {
    const { queryByTestId } = render(<LoadingOverlay visible={false} />);
    expect(queryByTestId('loading-overlay')).toBeNull();
  });

  it('renders with custom message', () => {
    const message = 'Custom loading message';
    const { getByText } = render(
      <LoadingOverlay visible={true} message={message} />
    );
    expect(getByText(message)).toBeTruthy();
  });

  it('renders with default message when none provided', () => {
    const { getByText } = render(<LoadingOverlay visible={true} />);
    expect(getByText('Loading...')).toBeTruthy();
  });
});
