import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import ExpenseItem from '../ExpenseItem';

describe('ExpenseItem', () => {
  const mockExpense = {
    id: '1',
    amount: 50.00,
    description: 'Test expense',
    category: 'Food',
    date: '2023-01-01'
  };

  const mockDelete = jest.fn();
  const mockEdit = jest.fn();

  it('renders expense details correctly', () => {
    const { getByText } = render(
      <ExpenseItem 
        expense={mockExpense}
        onDelete={mockDelete}
        onEdit={mockEdit}
      />
    );

    expect(getByText('$50.00')).toBeTruthy();
    expect(getByText('Test expense')).toBeTruthy();
    expect(getByText('Food')).toBeTruthy();
    expect(getByText('Jan 1, 2023')).toBeTruthy();
  });

  it('calls onDelete when delete button is pressed', () => {
    const { getByTestId } = render(
      <ExpenseItem 
        expense={mockExpense}
        onDelete={mockDelete}
        onEdit={mockEdit}
      />
    );

    fireEvent.press(getByTestId('delete-button'));
    expect(mockDelete).toHaveBeenCalledWith(mockExpense.id);
  });

  it('calls onEdit when edit button is pressed', () => {
    const { getByTestId } = render(
      <ExpenseItem 
        expense={mockExpense}
        onDelete={mockDelete}
        onEdit={mockEdit}
      />
    );

    fireEvent.press(getByTestId('edit-button'));
    expect(mockEdit).toHaveBeenCalledWith(mockExpense);
  });

  it('formats amount correctly', () => {
    const expenseWithDecimal = {
      ...mockExpense,
      amount: 50.99
    };

    const { getByText } = render(
      <ExpenseItem 
        expense={expenseWithDecimal}
        onDelete={mockDelete}
        onEdit={mockEdit}
      />
    );

    expect(getByText('$50.99')).toBeTruthy();
  });
});
