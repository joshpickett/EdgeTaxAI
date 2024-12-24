import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import { Alert } from 'react-native';
import { useDispatch, useSelector } from 'react-redux';
import SignupScreen from '../../screens/SignupScreen';

// Mock dependencies
jest.mock('react-redux', () => ({
  useDispatch: jest.fn(),
  useSelector: jest.fn(),
}));

describe('SignupScreen', () => {
  const mockDispatch = jest.fn();
  const mockNavigate = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    useDispatch.mockReturnValue(mockDispatch);
    useSelector.mockReturnValue({ loading: false, error: null, otpSent: false });
    Alert.alert = jest.fn();
  });

  it('renders correctly', () => {
    const { getByPlaceholderText, getByText } = render(
      <SignupScreen navigation={{ navigate: mockNavigate }} />
    );

    expect(getByPlaceholderText('Enter your email')).toBeTruthy();
    expect(getByPlaceholderText('Enter your phone')).toBeTruthy();
    expect(getByText('Sign Up')).toBeTruthy();
  });

  it('validates email format', async () => {
    const { getByPlaceholderText, getByText } = render(
      <SignupScreen navigation={{ navigate: mockNavigate }} />
    );

    fireEvent.changeText(getByPlaceholderText('Enter your email'), 'invalid-email');
    fireEvent.press(getByText('Sign Up'));

    await waitFor(() => {
      expect(getByText('Invalid email format')).toBeTruthy();
    });
  });

  it('validates phone format', async () => {
    const { getByPlaceholderText, getByText } = render(
      <SignupScreen navigation={{ navigate: mockNavigate }} />
    );

    fireEvent.changeText(getByPlaceholderText('Enter your phone'), '123');
    fireEvent.press(getByText('Sign Up'));

    await waitFor(() => {
      expect(getByText('Invalid phone format')).toBeTruthy();
    });
  });

  it('requires either email or phone', async () => {
    const { getByText } = render(
      <SignupScreen navigation={{ navigate: mockNavigate }} />
    );

    fireEvent.press(getByText('Sign Up'));

    await waitFor(() => {
      expect(getByText('Please enter either email or phone number')).toBeTruthy();
    });
  });

  it('handles successful signup', async () => {
    mockDispatch.mockResolvedValueOnce({ unwrap: () => ({ success: true }) });

    const { getByPlaceholderText, getByText } = render(
      <SignupScreen navigation={{ navigate: mockNavigate }} />
    );

    fireEvent.changeText(getByPlaceholderText('Enter your email'), 'test@example.com');
    fireEvent.press(getByText('Sign Up'));

    await waitFor(() => {
      expect(Alert.alert).toHaveBeenCalledWith('Success', 'OTP sent successfully!');
    });
  });

  it('handles signup failure', async () => {
    mockDispatch.mockRejectedValueOnce(new Error('Signup failed'));

    const { getByPlaceholderText, getByText } = render(
      <SignupScreen navigation={{ navigate: mockNavigate }} />
    );

    fireEvent.changeText(getByPlaceholderText('Enter your email'), 'test@example.com');
    fireEvent.press(getByText('Sign Up'));

    await waitFor(() => {
      expect(Alert.alert).toHaveBeenCalledWith('Error', 'Signup failed');
    });
  });

  it('shows OTP input after successful signup', async () => {
    useSelector.mockReturnValue({ loading: false, error: null, otpSent: true });

    const { getByPlaceholderText, getByText } = render(
      <SignupScreen navigation={{ navigate: mockNavigate }} />
    );

    expect(getByPlaceholderText('Enter OTP')).toBeTruthy();
    expect(getByText(/Enter the OTP sent to/)).toBeTruthy();
  });

  it('cleans up on unmount', () => {
    const { unmount } = render(
      <SignupScreen navigation={{ navigate: mockNavigate }} />
    );

    unmount();
    expect(mockDispatch).toHaveBeenCalledWith(expect.any(Function));
  });
});
