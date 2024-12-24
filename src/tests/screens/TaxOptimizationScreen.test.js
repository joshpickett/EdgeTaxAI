import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import { Alert } from 'react-native';
import TaxOptimizationScreen from '../../screens/TaxOptimizationScreen';
import { getTaxSavings, getDeductionSuggestions } from '../../services/taxService';

// Mock the services
jest.mock('../../services/taxService');

describe('TaxOptimizationScreen', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    getTaxSavings.mockResolvedValue(100);
    getDeductionSuggestions.mockResolvedValue([
      { description: 'Suggestion 1', amount: 50 },
      { description: 'Suggestion 2', amount: 75 },
    ]);
  });

  it('renders correctly', () => {
    const { getByText, getByPlaceholderText } = render(<TaxOptimizationScreen />);
    expect(getByText('Tax Optimization')).toBeTruthy();
    expect(getByPlaceholderText('Enter expense amount')).toBeTruthy();
  });

  it('handles empty amount input', async () => {
    const { getByText } = render(<TaxOptimizationScreen />);
    
    fireEvent.press(getByText('Calculate Tax Savings'));
    
    await waitFor(() => {
      expect(Alert.alert).toHaveBeenCalledWith('Error', 'Please enter an amount.');
    });
  });

  it('calculates tax savings successfully', async () => {
    const { getByText, getByPlaceholderText } = render(<TaxOptimizationScreen />);
    
    fireEvent.changeText(getByPlaceholderText('Enter expense amount'), '1000');
    fireEvent.press(getByText('Calculate Tax Savings'));

    await waitFor(() => {
      expect(getTaxSavings).toHaveBeenCalledWith('1000');
      expect(getByText('Estimated Tax Savings: $100.00')).toBeTruthy();
    });
  });

  it('fetches deduction suggestions successfully', async () => {
    const { getByText, getByPlaceholderText } = render(<TaxOptimizationScreen />);
    
    fireEvent.changeText(getByPlaceholderText('Enter expense amount'), '1000');
    fireEvent.press(getByText('Fetch Deduction Suggestions'));

    await waitFor(() => {
      expect(getDeductionSuggestions).toHaveBeenCalled();
      expect(getByText('Suggestion 1: $50')).toBeTruthy();
      expect(getByText('Suggestion 2: $75')).toBeTruthy();
    });
  });

  it('handles API errors gracefully', async () => {
    getTaxSavings.mockRejectedValue(new Error('API Error'));
    
    const { getByText, getByPlaceholderText } = render(<TaxOptimizationScreen />);
    
    fireEvent.changeText(getByPlaceholderText('Enter expense amount'), '1000');
    fireEvent.press(getByText('Calculate Tax Savings'));

    await waitFor(() => {
      expect(Alert.alert).toHaveBeenCalledWith('Error', expect.any(String));
    });
  });

  it('displays loading state while fetching tax rate', async () => {
    const { getByText } = render(<TaxOptimizationScreen />);
    expect(getByText('Fetching tax rate...')).toBeTruthy();
  });

  it('validates numeric input', async () => {
    const { getByText, getByPlaceholderText } = render(<TaxOptimizationScreen />);
    
    fireEvent.changeText(getByPlaceholderText('Enter expense amount'), 'invalid');
    fireEvent.press(getByText('Calculate Tax Savings'));

    await waitFor(() => {
      expect(Alert.alert).toHaveBeenCalledWith('Error', expect.any(String));
    });
  });
});
