import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import { setupSrcPath } from '../../setup_path';
import InputField from '../InputField';
import { colors, spacing } from '../../styles/tokens';

describe('InputField', () => {
  const defaultProps = {
    label: 'Test Label',
    placeholder: 'Test Placeholder',
    value: '',
    onChangeText: jest.fn()
  };

  it('renders correctly with required props', () => {
    const { getByText, getByPlaceholderText } = render(
      <InputField {...defaultProps} />
    );

    expect(getByText('Test Label')).toBeTruthy();
    expect(getByPlaceholderText('Test Placeholder')).toBeTruthy();
  });

  it('handles text input changes', () => {
    const onChangeText = jest.fn();
    const { getByPlaceholderText } = render(
      <InputField {...defaultProps} onChangeText={onChangeText} />
    );

    fireEvent.changeText(getByPlaceholderText('Test Placeholder'), 'test input');
    expect(onChangeText).toHaveBeenCalledWith('test input');
  });

  it('displays error message when error prop is provided', () => {
    const { getByText } = render(
      <InputField {...defaultProps} error="Test error message" />
    );

    expect(getByText('Test error message')).toBeTruthy();
  });

  it('applies error styles when error prop is provided', () => {
    const { getByPlaceholderText } = render(
      <InputField {...defaultProps} error="Test error" />
    );

    const input = getByPlaceholderText('Test Placeholder');
    expect(input.props.style).toContainEqual(
      expect.objectContaining({ borderColor: colors.error.main }));
  });

  it('handles secure text entry', () => {
    const { getByPlaceholderText } = render(
      <InputField {...defaultProps} secureTextEntry={true} />
    );

    const input = getByPlaceholderText('Test Placeholder');
    expect(input.props.secureTextEntry).toBeTruthy();
  });
});
