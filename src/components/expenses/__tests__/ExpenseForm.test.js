import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import ExpenseForm from '../ExpenseForm';

describe('ExpenseForm', () => {
  const mockSubmit = jest.fn();

  beforeEach(() => {
    mockSubmit.mockClear();
  });

  it('renders all form fields', () => {
    const { getByPlaceholderText, getByText } = render(
      <ExpenseForm onSubmit={mockSubmit} />
    );

    expect(getByPlaceholderText('Amount')).toBeTruthy();
    expect(getByPlaceholderText('Description')).toBeTruthy();
    expect(getByPlaceholderText('Category')).toBeTruthy();
    expect(getByText('Submit')).toBeTruthy();
  });

  it('validates required fields', async () => {
    const { getByText } = render(<ExpenseForm onSubmit={mockSubmit} />);
    
    fireEvent.press(getByText('Submit'));

    await waitFor(() => {
      expect(getByText('Amount is required')).toBeTruthy();
      expect(getByText('Description is required')).toBeTruthy();
    });
  });

  it('validates amount format', async () => {
    const { getByPlaceholderText, getByText } = render(
      <ExpenseForm onSubmit={mockSubmit} />
    );

    fireEvent.changeText(getByPlaceholderText('Amount'), 'invalid');
    fireEvent.press(getByText('Submit'));

    await waitFor(() => {
      expect(getByText('Amount must be a valid number')).toBeTruthy();
    });
  });

  it('submits form with valid data', async () => {
    const { getByPlaceholderText, getByText } = render(
      <ExpenseForm onSubmit={mockSubmit} />
    );

    fireEvent.changeText(getByPlaceholderText('Amount'), '50.00');
    fireEvent.changeText(getByPlaceholderText('Description'), 'Test expense');
    fireEvent.changeText(getByPlaceholderText('Category'), 'Food');
    
    fireEvent.press(getByText('Submit'));

    await waitFor(() => {
      expect(mockSubmit).toHaveBeenCalledWith({
        amount: 50.00,
        description: 'Test expense',
        category: 'Food'
      });
    });
  });
});
