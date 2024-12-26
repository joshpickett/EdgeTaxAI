import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import { Provider } from 'react-redux';
import configureStore from 'redux-mock-store';
import SignupScreen from '../SignupScreen';
import { signupUser, verifyOTP } from '../../store/slices/authSlice';

const mockStore = configureStore([]);

describe('SignupScreen', () => {
  let store;

  beforeEach(() => {
    store = mockStore({
      auth: {
        loading: false,
        error: null,
        otpSent: false
      }
    });
    store.dispatch = jest.fn();
  });

  it('renders signup form correctly', () => {
    const { getByPlaceholderText, getByText } = render(
      <Provider store={store}>
        <SignupScreen />
      </Provider>
    );

    expect(getByPlaceholderText('Enter your email')).toBeTruthy();
    expect(getByPlaceholderText('Enter your phone')).toBeTruthy();
    expect(getByText('Sign Up')).toBeTruthy();
  });

  it('validates email format', async () => {
    const { getByPlaceholderText, getByText, findByText } = render(
      <Provider store={store}>
        <SignupScreen />
      </Provider>
    );

    fireEvent.changeText(getByPlaceholderText('Enter your email'), 'invalid-email');
    fireEvent.press(getByText('Sign Up'));

    expect(await findByText('Invalid email format')).toBeTruthy();
  });

  it('validates phone format', async () => {
    const { getByPlaceholderText, getByText, findByText } = render(
      <Provider store={store}>
        <SignupScreen />
      </Provider>
    );

    fireEvent.changeText(getByPlaceholderText('Enter your phone'), '123');
    fireEvent.press(getByText('Sign Up'));

    expect(await findByText('Invalid phone format')).toBeTruthy();
  });

  it('handles successful signup', async () => {
    store.dispatch.mockResolvedValueOnce({ payload: { success: true } });

    const { getByPlaceholderText, getByText } = render(
      <Provider store={store}>
        <SignupScreen />
      </Provider>
    );

    fireEvent.changeText(getByPlaceholderText('Enter your email'), 'test@example.com');
    fireEvent.press(getByText('Sign Up'));

    await waitFor(() => {
      expect(store.dispatch).toHaveBeenCalledWith(
        expect.objectContaining({
          type: expect.stringContaining('signupUser')
        })
      );
    });
  });

  it('displays OTP input after successful signup', async () => {
    store = mockStore({
      auth: {
        loading: false,
        error: null,
        otpSent: true
      }
    });

    const { getByPlaceholderText } = render(
      <Provider store={store}>
        <SignupScreen />
      </Provider>
    );

    expect(getByPlaceholderText('Enter OTP')).toBeTruthy();
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
        <SignupScreen />
      </Provider>
    );

    fireEvent.changeText(getByPlaceholderText('Enter OTP'), '123456');
    fireEvent.press(getByText('Verify OTP'));

    await waitFor(() => {
      expect(store.dispatch).toHaveBeenCalledWith(
        expect.objectContaining({
          type: expect.stringContaining('verifyOTP')
        })
      );
    });
  });
});
