import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import ExpensesScreen from '../ExpensesScreen';
import { expenseService } from '../../services/expenseService';

jest.mock('../../services/expenseService');
jest.mock('expo-image-picker');

describe('ExpensesScreen', () => {
  beforeEach(() => {
    expenseService.addExpense.mockClear();
    expenseService.processReceipt.mockClear();
  });

  it('renders expense form correctly', () => {
    const { getByPlaceholderText, getByText } = render(<ExpensesScreen />);
    
    expect(getByPlaceholderText('Description')).toBeTruthy();
    expect(getByPlaceholderText('Amount')).toBeTruthy();
    expect(getByText('Add Expense')).toBeTruthy();
  });

  it('validates form inputs', async () => {
    const { getByText, getByPlaceholderText } = render(<ExpensesScreen />);
    
    fireEvent.press(getByText('Add Expense'));
    
    await waitFor(() => {
      expect(getByText('Description is required')).toBeTruthy();
      expect(getByText('Amount is required')).toBeTruthy();
    });
  });

  it('handles expense submission', async () => {
    const { getByText, getByPlaceholderText } = render(<ExpensesScreen />);
    
    fireEvent.changeText(getByPlaceholderText('Description'), 'Test Expense');
    fireEvent.changeText(getByPlaceholderText('Amount'), '50.00');
    fireEvent.press(getByText('Add Expense'));

    await waitFor(() => {
      expect(expenseService.addExpense).toHaveBeenCalledWith({
        description: 'Test Expense',
        amount: 50.00
      });
    });
  });

  it('handles receipt upload', async () => {
    const mockReceiptData = {
      description: 'Receipt Item',
      amount: 75.00
    };
    expenseService.processReceipt.mockResolvedValue(mockReceiptData);

    const { getByText, getByPlaceholderText } = render(<ExpensesScreen />);
    fireEvent.press(getByText('Upload Receipt'));

    await waitFor(() => {
      expect(getByPlaceholderText('Description').props.value).toBe('Receipt Item');
      expect(getByPlaceholderText('Amount').props.value).toBe('75.00');
    });
  });
});
