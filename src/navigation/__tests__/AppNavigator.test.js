import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import { NavigationContainer } from '@react-navigation/native';
import { Provider } from 'react-redux';
import configureStore from 'redux-mock-store';
import AppNavigator from '../AppNavigator';
import { logoutUser } from '../../services/api';

jest.mock('../../services/api');
jest.mock('@react-native-async-storage/async-storage', () => ({
  removeItem: jest.fn()
}));

const mockStore = configureStore([]);

describe('AppNavigator', () => {
  let store;

  beforeEach(() => {
    store = mockStore({
      auth: {
        isAuthenticated: false
      }
    });
  });

  it('renders auth stack when not authenticated', () => {
    const { getByText } = render(
      <Provider store={store}>
        <NavigationContainer>
          <AppNavigator />
        </NavigationContainer>
      </Provider>
    );

    expect(getByText('Login')).toBeTruthy();
  });

  it('renders main stack when authenticated', () => {
    store = mockStore({
      auth: {
        isAuthenticated: true
      }
    });

    const { getByText } = render(
      <Provider store={store}>
        <NavigationContainer>
          <AppNavigator />
        </NavigationContainer>
      </Provider>
    );

    expect(getByText('Dashboard')).toBeTruthy();
  });

  it('handles logout correctly', async () => {
    logoutUser.mockResolvedValueOnce();
    store = mockStore({
      auth: {
        isAuthenticated: true
      }
    });

    const { getByText } = render(
      <Provider store={store}>
        <NavigationContainer>
          <AppNavigator />
        </NavigationContainer>
      </Provider>
    );

    await fireEvent.press(getByText('Logout'));
    expect(logoutUser).toHaveBeenCalled();
  });
});
