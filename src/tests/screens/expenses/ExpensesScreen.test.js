import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import ExpensesScreen from '../../../screens/expenses/ExpensesScreen';
import { listExpenses, editExpense, deleteExpense } from '../../../services/expenseService';

// Mock the service functions
jest.mock('../../../services/expenseService');

describe('ExpensesScreen', () => {
  const mockExpenses = [
    { id: 1, description: 'Test Expense 1', amount: 100, category: 'Food', date: '2023-01-01' },
    { id: 2, description: 'Test Expense 2', amount: 200, category: 'Transport', date: '2023-01-02' },
  ];

  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
    // Setup default successful response
    listExpenses.mockResolvedValue(mockExpenses);
  });

  it('renders loading state initially', () => {
    const { getByTestId } = render(<ExpensesScreen userId="123" />);
    expect(getByTestId('loading-indicator')).toBeTruthy();
  });

  it('renders expenses list after loading', async () => {
    const { getByText } = render(<ExpensesScreen userId="123" />);
    await waitFor(() => {
      expect(getByText('Test Expense 1')).toBeTruthy();
      expect(getByText('Test Expense 2')).toBeTruthy();
    });
  });

  it('handles edit expense correctly', async () => {
    const { getByText, getByPlaceholderText } = render(<ExpensesScreen userId="123" />);
    
    await waitFor(() => {
      fireEvent.press(getByText('Edit'));
    });

    fireEvent.changeText(getByPlaceholderText('Description'), 'Updated Expense');
    fireEvent.changeText(getByPlaceholderText('Amount'), '150');
    fireEvent.press(getByText('Save'));

    expect(editExpense).toHaveBeenCalledWith(1, {
      description: 'Updated Expense',
      amount: 150,
    });
  });

  it('handles delete expense correctly', async () => {
    const { getByText } = render(<ExpensesScreen userId="123" />);
    
    await waitFor(() => {
      fireEvent.press(getByText('Delete'));
    });

    fireEvent.press(getByText('Delete')); // Confirm deletion

    expect(deleteExpense).toHaveBeenCalledWith(1);
  });

  it('shows error message when API fails', async () => {
    listExpenses.mockRejectedValue(new Error('API Error'));
    
    const { getByText } = render(<ExpensesScreen userId="123" />);
    
    await waitFor(() => {
      expect(getByText('Failed to load expenses.')).toBeTruthy();
    });
  });

  it('handles empty expenses list', async () => {
    listExpenses.mockResolvedValue([]);
    
    const { getByText } = render(<ExpensesScreen userId="123" />);
    
    await waitFor(() => {
      expect(getByText('No expenses found.')).toBeTruthy();
    });
  });
});
