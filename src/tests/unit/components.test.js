import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import { useSelector, useDispatch } from 'react-redux';
import { NavigationContainer } from '@react-navigation/native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useAuth } from '../../hooks/useAuth';
import AppNavigator from '../../navigation/AppNavigator';
import LoginScreen from '../../screens/LoginScreen'; // Assuming these imports exist
import DashboardScreen from '../../screens/DashboardScreen'; // Assuming these imports exist
import ExpensesScreen from '../../screens/ExpensesScreen'; // Assuming these imports exist

// Mock the dependencies
jest.mock('react-redux');
jest.mock('@react-native-async-storage/async-storage');
jest.mock('../../services/api');

// Test useAuth hook
describe('useAuth Hook', () => {
    const mockDispatch = jest.fn();
    const mockSelector = jest.fn();

    beforeEach(() => {
        useDispatch.mockReturnValue(mockDispatch);
        useSelector.mockImplementation(mockSelector);
        mockDispatch.mockClear();
        mockSelector.mockClear();
    });

    test('login success', async () => {
        mockDispatch.mockResolvedValueOnce({ unwrap: () => Promise.resolve(true) });
        const { login } = useAuth();
        const result = await login('test@example.com');
        expect(result).toBe(true);
        expect(mockDispatch).toHaveBeenCalled();
    });

    test('login failure', async () => {
        mockDispatch.mockResolvedValueOnce({ unwrap: () => Promise.reject(new Error()) });
        const { login } = useAuth();
        const result = await login('test@example.com');
        expect(result).toBe(false);
    });

    test('verify OTP success', async () => {
        mockDispatch.mockResolvedValueOnce({ unwrap: () => Promise.resolve(true) });
        const { verify } = useAuth();
        const result = await verify('test@example.com', '123456');
        expect(result).toBe(true);
    });

    test('logout', () => {
        const { logout } = useAuth();
        logout();
        expect(mockDispatch).toHaveBeenCalled();
    });
});

// Test AppNavigator
describe('AppNavigator', () => {
    beforeEach(() => {
        AsyncStorage.getItem.mockClear();
        AsyncStorage.removeItem.mockClear();
    });

    test('renders login screen initially', () => {
        const { getByText } = render(
            <NavigationContainer>
                <AppNavigator />
            </NavigationContainer>
        );
        expect(getByText('Login')).toBeTruthy();
    });

    test('handles logout', async () => {
        const { getByText } = render(
            <NavigationContainer>
                <AppNavigator />
            </NavigationContainer>
        );
        
        const logoutButton = getByText('Logout');
        fireEvent.press(logoutButton);
        
        await waitFor(() => {
            expect(AsyncStorage.removeItem).toHaveBeenCalledWith('userToken');
        });
    });

    test('navigates to signup', () => {
        const { getByText } = render(
            <NavigationContainer>
                <AppNavigator />
            </NavigationContainer>
        );
        
        const signupLink = getByText("Don't have an account? Sign Up");
        fireEvent.press(signupLink);
        
        expect(getByText('Sign Up')).toBeTruthy();
    });

    test('protected route redirect', async () => {
        AsyncStorage.getItem.mockResolvedValueOnce(null);
        
        const { getByText } = render(
            <NavigationContainer>
                <AppNavigator />
            </NavigationContainer>
        );
        
        // Attempt to navigate to protected route
        const dashboardLink = getByText('Dashboard');
        fireEvent.press(dashboardLink);
        
        // Should redirect to login
        await waitFor(() => {
            expect(getByText('Login')).toBeTruthy();
        });
    });
});

// Test Screen Components
describe('Screen Components', () => {
    test('LoginScreen renders correctly', () => {
        const { getByPlaceholderText, getByText } = render(<LoginScreen />);
        expect(getByPlaceholderText('Email or Phone')).toBeTruthy();
        expect(getByText('Send OTP')).toBeTruthy();
    });

    test('DashboardScreen renders correctly', () => {
        const { getByText } = render(<DashboardScreen />);
        expect(getByText('Dashboard')).toBeTruthy();
    });

    test('ExpensesScreen renders correctly', () => {
        const { getByText } = render(<ExpensesScreen />);
        expect(getByText('Add Expense')).toBeTruthy();
    });

    // Add more screen component tests...
});

// Test Navigation Flow
describe('Navigation Flow', () => {
    test('login to dashboard flow', async () => {
        const { getByText, getByPlaceholderText } = render(
            <NavigationContainer>
                <AppNavigator />
            </NavigationContainer>
        );

        // Fill login form
        fireEvent.changeText(getByPlaceholderText('Email or Phone'), 'test@example.com');
        fireEvent.press(getByText('Send OTP'));

        // Verify OTP
        fireEvent.changeText(getByPlaceholderText('Enter OTP'), '123456');
        fireEvent.press(getByText('Verify OTP'));

        // Should navigate to dashboard
        await waitFor(() => {
            expect(getByText('Dashboard')).toBeTruthy();
        });
    });
});
