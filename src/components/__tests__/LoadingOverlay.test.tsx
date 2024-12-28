import React from 'react';
import { render } from '@testing-library/react-native';
import { setupSrcPath } from '../../setup_path';
import LoadingOverlay from '../LoadingOverlay';
import { colors } from '../../styles/tokens';

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

  it('uses custom color when provided', () => {
    const customColor = '#FF0000';
    const { getByTestId } = render(
      <LoadingOverlay color={colors.error.main} />
    );
    const spinner = getByTestId('loading-spinner');
    expect(spinner.props.color).toBe(customColor);
  });
});
