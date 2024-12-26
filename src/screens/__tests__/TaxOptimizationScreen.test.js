import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import TaxOptimizationScreen from '../TaxOptimizationScreen';
import { getTaxSavings, getDeductionSuggestions } from '../../services/taxService';

jest.mock('../../services/taxService');

describe('TaxOptimizationScreen', () => {
  beforeEach(() => {
    getTaxSavings.mockClear();
    getDeductionSuggestions.mockClear();
  });

  it('renders correctly', () => {
    const { getByText, getByPlaceholderText } = render(<TaxOptimizationScreen />);
    expect(getByText('Tax Optimization')).toBeTruthy();
    expect(getByPlaceholderText('Enter expense amount')).toBeTruthy();
  });

  it('handles tax savings calculation', async () => {
    getTaxSavings.mockResolvedValueOnce(500);
    
    const { getByText, getByPlaceholderText } = render(<TaxOptimizationScreen />);
    
    fireEvent.changeText(getByPlaceholderText('Enter expense amount'), '1000');
    fireEvent.press(getByText('Calculate Tax Savings'));

    await waitFor(() => {
      expect(getTaxSavings).toHaveBeenCalledWith('1000');
      expect(getByText('Estimated Tax Savings: $500.00')).toBeTruthy();
    });
  });

  it('handles deduction suggestions', async () => {
    const mockSuggestions = [
      { description: 'Test Deduction', amount: 100 }
    ];
    getDeductionSuggestions.mockResolvedValueOnce(mockSuggestions);

    const { getByText } = render(<TaxOptimizationScreen />);
    
    fireEvent.press(getByText('Fetch Deduction Suggestions'));

    await waitFor(() => {
      expect(getByText('Test Deduction: $100')).toBeTruthy();
    });
  });

  it('displays error for invalid input', async () => {
    const { getByText } = render(<TaxOptimizationScreen />);
    
    fireEvent.press(getByText('Calculate Tax Savings'));

    await waitFor(() => {
      expect(getByText('Please enter an amount.')).toBeTruthy();
    });
  });
});
