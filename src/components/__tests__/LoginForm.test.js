import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import { Provider } from 'react-redux';
import configureStore from 'redux-mock-store';
import LoginForm from '../LoginForm';
import { authService } from '../../services/authService';

jest.mock('../../services/authService');

describe('LoginForm', () => {
  const mockStore = configureStore([]);
  let store;

  beforeEach(() => {
    store = mockStore({
      auth: {
        loading: false,
        error: null
      }
    });
  });

  it('renders all form fields', () => {
    const { getByPlaceholderText, getByText } = render(
      <Provider store={store}>
        <LoginForm />
      </Provider>
    );

    expect(getByPlaceholderText('Email')).toBeTruthy();
    expect(getByPlaceholderText('Password')).toBeTruthy();
    expect(getByText('Login')).toBeTruthy();
  });

  it('validates required fields', async () => {
    const { getByText } = render(
      <Provider store={store}>
        <LoginForm />
      </Provider>
    );

    fireEvent.press(getByText('Login'));

    await waitFor(() => {
      expect(getByText('Email is required')).toBeTruthy();
      expect(getByText('Password is required')).toBeTruthy();
    });
  });

  it('validates email format', async () => {
    const { getByPlaceholderText, getByText } = render(
      <Provider store={store}>
        <LoginForm />
      </Provider>
    );

    fireEvent.changeText(getByPlaceholderText('Email'), 'invalid-email');
    fireEvent.press(getByText('Login'));

    await waitFor(() => {
      expect(getByText('Invalid email format')).toBeTruthy();
    });
  });

  it('handles successful login', async () => {
    const mockLogin = jest.fn();
    authService.login.mockResolvedValueOnce({ token: 'test-token' });

    const { getByPlaceholderText, getByText } = render(
      <Provider store={store}>
        <LoginForm onLogin={mockLogin} />
      </Provider>
    );

    fireEvent.changeText(getByPlaceholderText('Email'), 'test@example.com');
    fireEvent.changeText(getByPlaceholderText('Password'), 'password123');
    fireEvent.press(getByText('Login'));

    await waitFor(() => {
      expect(authService.login).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123'
      });
      expect(mockLogin).toHaveBeenCalled();
    });
  });

  it('handles login error', async () => {
    authService.login.mockRejectedValueOnce(new Error('Invalid credentials'));

    const { getByPlaceholderText, getByText } = render(
      <Provider store={store}>
        <LoginForm />
      </Provider>
    );

    fireEvent.changeText(getByPlaceholderText('Email'), 'test@example.com');
    fireEvent.changeText(getByPlaceholderText('Password'), 'password123');
    fireEvent.press(getByText('Login'));

    await waitFor(() => {
      expect(getByText('Invalid credentials')).toBeTruthy();
    });
  });
});
