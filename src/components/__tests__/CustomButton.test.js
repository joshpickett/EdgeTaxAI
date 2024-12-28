import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import { setupSrcPath } from '../../setup_path';
import CustomButton from '../CustomButton';
setupSrcPath();

describe('CustomButton', () => {
  it('renders correctly with title', () => {
    const { getByText } = render(<CustomButton title="Test Button" />);
    expect(getByText('Test Button')).toBeTruthy();
  });

  it('handles press events', () => {
    const onPressMock = jest.fn();
    const { getByText } = render(
      <CustomButton title="Test Button" onPress={onPressMock} />
    );
    
    fireEvent.press(getByText('Test Button'));
    expect(onPressMock).toHaveBeenCalled();
  });

  it('applies custom styles', () => {
    const { getByText } = render(
      <CustomButton title="Test Button" style={{ backgroundColor: 'red' }} />
    );
    const button = getByText('Test Button').parent;
    expect(button.props.style).toContainEqual({ backgroundColor: 'red' });
  });
});
