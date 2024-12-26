import React from 'react';
import { render } from '@testing-library/react-native';
import ErrorMessage from '../ErrorMessage';

describe('ErrorMessage', () => {
  it('renders error message correctly', () => {
    const message = 'Test error message';
    const { getByText } = render(<ErrorMessage message={message} />);
    expect(getByText(message)).toBeTruthy();
  });

  it('applies error style by default', () => {
    const { getByText } = render(<ErrorMessage message="Test" />);
    const container = getByText('Test').parent;
    expect(container.props.style).toContainEqual(expect.objectContaining({
      borderWidth: 1
    }));
  });

  it('applies success style when type is success', () => {
    const { getByText } = render(
      <ErrorMessage message="Test" type="success" />
    );
    const container = getByText('Test').parent;
    expect(container.props.style).toContainEqual(expect.objectContaining({
      borderWidth: 1
    }));
  });

  it('applies warning style when type is warning', () => {
    const { getByText } = render(
      <ErrorMessage message="Test" type="warning" />
    );
    const container = getByText('Test').parent;
    expect(container.props.style).toContainEqual(expect.objectContaining({
      borderWidth: 1
    }));
  });
});
