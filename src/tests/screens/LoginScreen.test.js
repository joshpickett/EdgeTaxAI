import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import { useDispatch, useSelector } from 'react-redux';
import LoginScreen from '../../screens/LoginScreen';
import { loginUser, verifyOTP, verifyBiometric } from '../../store/slices/authSlice';
import * as LocalAuthentication from 'expo-local-authentication';

// Mock dependencies
jest.mock('react-redux');
jest.mock('expo-local-authentication');
jest.mock('../../store/slices/authSlice');

describe('LoginScreen', () => {
  const mockDispatch = jest.fn();
  const mockNavigate = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    useDispatch.mockReturnValue(mockDispatch);
    useSelector.mockReturnValue({ loading: false, error: null, otpSent: false });
    LocalAuthentication.hasHardwareAsync.mockResolvedValue(true);
    LocalAuthentication.isEnrolledAsync.mockResolvedValue(true);
  });

  it('renders login form correctly', () => {
    const { getByPlaceholderText, getByText } = render(
      <LoginScreen navigation={{ navigate: mockNavigate }} />
    );

    expect(getByPlaceholderText('Email or Phone')).toBeTruthy();
    expect(getByText('Login with OTP')).toBeTruthy();
  });

  it('validates input before sending One Time Password', async () => {
    const { getByText, getByPlaceholderText } = render(
      <LoginScreen navigation={{ navigate: mockNavigate }} />
    );

    fireEvent.press(getByText('Send One Time Password'));
    expect(getByText('Email or phone is required')).toBeTruthy();

    fireEvent.changeText(getByPlaceholderText('Email or Phone'), 'invalid-email');
    fireEvent.press(getByText('Send One Time Password'));
    expect(getByText('Please enter a valid email or phone number')).toBeTruthy();
  });

  it('handles One Time Password verification successfully', async () => {
    loginUser.mockResolvedValue({ success: true });
    verifyOTP.mockResolvedValue({ success: true });

    const { getByText, getByPlaceholderText } = render(
      <LoginScreen navigation={{ navigate: mockNavigate }} />
    );

    fireEvent.changeText(getByPlaceholderText('Email or Phone'), 'test@example.com');
    fireEvent.press(getByText('Send One Time Password'));

    await waitFor(() => {
      expect(loginUser).toHaveBeenCalledWith({ identifier: 'test@example.com' });
    });

    fireEvent.changeText(getByPlaceholderText('Enter One Time Password'), '123456');
    fireEvent.press(getByText('Verify One Time Password'));

    await waitFor(() => {
      expect(verifyOTP).toHaveBeenCalledWith({
        identifier: 'test@example.com',
        otp: '123456'
      });
      expect(mockNavigate).toHaveBeenCalledWith('Dashboard');
    });
  });

  it('handles biometric authentication', async () => {
    LocalAuthentication.authenticateAsync.mockResolvedValue({ success: true });
    verifyBiometric.mockResolvedValue({ success: true });

    const { getByText } = render(
      <LoginScreen navigation={{ navigate: mockNavigate }} />
    );

    fireEvent.press(getByText('Login with Biometrics'));

    await waitFor(() => {
      expect(LocalAuthentication.authenticateAsync).toHaveBeenCalled();
      expect(verifyBiometric).toHaveBeenCalled();
      expect(mockNavigate).toHaveBeenCalledWith('Dashboard');
    });
  });

  it('handles error states appropriately', async () => {
    loginUser.mockRejectedValue(new Error('Authentication failed'));

    const { getByText, getByPlaceholderText } = render(
      <LoginScreen navigation={{ navigate: mockNavigate }} />
    );

    fireEvent.changeText(getByPlaceholderText('Email or Phone'), 'test@example.com');
    fireEvent.press(getByText('Send One Time Password'));

    await waitFor(() => {
      expect(getByText('Authentication failed')).toBeTruthy();
    });
  });

  it('navigates to signup screen', () => {
    const { getByText } = render(
      <LoginScreen navigation={{ navigate: mockNavigate }} />
    );

    fireEvent.press(getByText("Don't have an account? Sign Up"));
    expect(mockNavigate).toHaveBeenCalledWith('Signup');
  });
});
