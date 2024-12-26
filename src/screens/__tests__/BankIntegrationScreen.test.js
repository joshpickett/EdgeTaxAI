import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import BankIntegrationScreen from '../BankIntegrationScreen';
import { bankService } from '../../services/bankService';

jest.mock('../../services/bankService');

describe('BankIntegrationScreen', () => {
  beforeEach(() => {
    bankService.connectBank.mockClear();
    bankService.fetchTransactions.mockClear();
  });

  it('renders correctly', () => {
    const { getByText, getByPlaceholderText } = render(<BankIntegrationScreen />);
    expect(getByText('Bank Integration')).toBeTruthy();
    expect(getByPlaceholderText('Enter Bank Name')).toBeTruthy();
  });

  it('handles bank connection', async () => {
    const { getByText, getByPlaceholderText } = render(<BankIntegrationScreen />);
    
    fireEvent.changeText(getByPlaceholderText('Enter Bank Name'), 'Test Bank');
    fireEvent.press(getByText('Connect Bank'));

    await waitFor(() => {
      expect(bankService.connectBank).toHaveBeenCalledWith('Test Bank');
    });
  });

  it('handles error states', async () => {
    bankService.connectBank.mockRejectedValue(new Error('Connection failed'));
    
    const { getByText, getByPlaceholderText } = render(<BankIntegrationScreen />);
    
    fireEvent.changeText(getByPlaceholderText('Enter Bank Name'), 'Test Bank');
    fireEvent.press(getByText('Connect Bank'));

    await waitFor(() => {
      expect(getByText('Connection failed')).toBeTruthy();
    });
  });

  it('displays transaction history', async () => {
    const mockTransactions = [
      { id: 1, amount: 100, description: 'Test Transaction' }
    ];
    bankService.fetchTransactions.mockResolvedValue(mockTransactions);

    const { getByText } = render(<BankIntegrationScreen />);
    fireEvent.press(getByText('View Transactions'));

    await waitFor(() => {
      expect(getByText('Test Transaction')).toBeTruthy();
      expect(getByText('$100')).toBeTruthy();
    });
  });
});
