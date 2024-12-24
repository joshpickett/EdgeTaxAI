import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import ExpenseDashboardScreen from '../../screens/expenses/ExpenseDashboardScreen';
import { listExpenses } from '../../services/expenseService';

// Mock the dependencies
jest.mock('../../services/expenseService');

describe('ExpenseDashboardScreen', () => {
    const mockUserId = '123';

    beforeEach(() => {
        jest.clearAllMocks();
    });

    test('renders loading state initially', () => {
        const { getByTestId } = render(
            <ExpenseDashboardScreen userId={mockUserId} />
        );
        expect(getByTestId('loading-indicator')).toBeTruthy();
    });

    test('renders expenses list successfully', async () => {
        const mockExpenses = [
            { id: 1, description: 'Test Expense', amount: 100, category: 'Food', date: '2023-01-01' }
        ];
        
        listExpenses.mockResolvedValueOnce(mockExpenses);

        const { getByText } = render(
            <ExpenseDashboardScreen userId={mockUserId} />
        );

        await waitFor(() => {
            expect(getByText('Test Expense - $100 (Food)')).toBeTruthy();
            expect(getByText('Date: 2023-01-01')).toBeTruthy();
        });
    });

    test('handles empty expenses list', async () => {
        listExpenses.mockResolvedValueOnce([]);

        const { getByText } = render(
            <ExpenseDashboardScreen userId={mockUserId} />
        );

        await waitFor(() => {
            expect(getByText('No expenses found.')).toBeTruthy();
        });
    });

    test('handles error state', async () => {
        listExpenses.mockRejectedValueOnce(new Error('Failed to load expenses'));

        const { getByText } = render(
            <ExpenseDashboardScreen userId={mockUserId} />
        );

        await waitFor(() => {
            expect(getByText('Failed to load expenses. Please try again.')).toBeTruthy();
        });
    });

    test('refresh functionality works', async () => {
        const mockExpenses = [
            { id: 1, description: 'Test Expense', amount: 100, category: 'Food', date: '2023-01-01' }
        ];
        
        listExpenses.mockResolvedValueOnce(mockExpenses);

        const { getByText } = render(
            <ExpenseDashboardScreen userId={mockUserId} />
        );

        await waitFor(() => {
            const refreshButton = getByText('Refresh');
            fireEvent.press(refreshButton);
            expect(listExpenses).toHaveBeenCalledTimes(2);
        });
    });

    test('expense item renders correctly', async () => {
        const mockExpenses = [
            { id: 1, description: 'Test Expense', amount: 100, category: 'Food', date: '2023-01-01' }
        ];
        
        listExpenses.mockResolvedValueOnce(mockExpenses);

        const { getByTestId } = render(
            <ExpenseDashboardScreen userId={mockUserId} />
        );

        await waitFor(() => {
            const expenseItem = getByTestId('expense-item-1');
            expect(expenseItem).toBeTruthy();
        });
    });
});
