import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import { Provider } from 'react-redux';
import configureStore from 'redux-mock-store';
import LoginScreen from '../LoginScreen';
import * as LocalAuthentication from 'expo-local-authentication';

jest.mock('expo-local-authentication');

const mockStore = configureStore([]);

describe('LoginScreen', () => {
  let store;

  beforeEach(() => {
    store = mockStore({
      auth: {
        loading: false,
        error: null,
        otpSent: false
      }
    });
    
    LocalAuthentication.hasHardwareAsync.mockResolvedValue(true);
    LocalAuthentication.isEnrolledAsync.mockResolvedValue(true);
  });

  it('renders login form correctly', () => {
    const { getByPlaceholderText, getByText } = render(
      <Provider store={store}>
        <LoginScreen />
      </Provider>
    );

    expect(getByPlaceholderText('Email or Phone')).toBeTruthy();
    expect(getByText('Send OTP')).toBeTruthy();
  });

  it('validates input before sending OTP', async () => {
    const { getByText } = render(
      <Provider store={store}>
        <LoginScreen />
      </Provider>
    );

    fireEvent.press(getByText('Send OTP'));

    await waitFor(() => {
      expect(getByText('Please enter a valid email or phone number')).toBeTruthy();
    });
  });

  it('handles OTP verification', async () => {
    store = mockStore({
      auth: {
        loading: false,
        error: null,
        otpSent: true
      }
    });

    const { getByPlaceholderText, getByText } = render(
      <Provider store={store}>
        <LoginScreen />
      </Provider>
    );

    fireEvent.changeText(getByPlaceholderText('Enter OTP'), '123456');
    fireEvent.press(getByText('Verify OTP'));

    const actions = store.getActions();
    expect(actions).toContainEqual(
      expect.objectContaining({
        type: expect.stringContaining('verifyOTP')
      })
    );
  });

  it('handles biometric authentication', async () => {
    LocalAuthentication.authenticateAsync.mockResolvedValueOnce({
      success: true
    });

    const { getByText } = render(
      <Provider store={store}>
        <LoginScreen />
      </Provider>
    );

    fireEvent.press(getByText('Login with Biometrics'));

    await waitFor(() => {
      expect(LocalAuthentication.authenticateAsync).toHaveBeenCalled();
    });
  });

  it('displays loading state', () => {
    store = mockStore({
      auth: {
        loading: true,
        error: null,
        otpSent: false
      }
    });

    const { getByTestId } = render(
      <Provider store={store}>
        <LoginScreen />
      </Provider>
    );

    expect(getByTestId('loading-indicator')).toBeTruthy();
  });
});
