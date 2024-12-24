import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import BankIntegrationScreen from '../../screens/BankIntegrationScreen';
import { bankService } from '../../services/bankService';

// Mock the bankService
jest.mock('../../services/bankService');

describe('BankIntegrationScreen', () => {
  const mockUserId = '123';
  const mockTransactions = [
    { id: 1, date: '2023-01-01', description: 'Transaction 1', amount: 100 },
    { id: 2, date: '2023-01-02', description: 'Transaction 2', amount: 200 },
  ];

  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
    
    // Setup default successful responses
    bankService.getLinkToken.mockResolvedValue({ message: 'Success' });
    bankService.getTransactions.mockResolvedValue({ transactions: mockTransactions });
    bankService.getBalance.mockResolvedValue({ balance: 1000 });
  });

  it('renders correctly', () => {
    const { getByText, getByPlaceholderText } = render(
      <BankIntegrationScreen userId={mockUserId} />
    );
    
    expect(getByText('Bank Integration')).toBeTruthy();
    expect(getByPlaceholderText('Enter Bank Name')).toBeTruthy();
    expect(getByText('Connect Bank Account')).toBeTruthy();
  });

  it('handles bank connection successfully', async () => {
    const { getByText, getByPlaceholderText } = render(
      <BankIntegrationScreen userId={mockUserId} />
    );

    fireEvent.changeText(getByPlaceholderText('Enter Bank Name'), 'Test Bank');
    fireEvent.press(getByText('Connect Bank Account'));

    await waitFor(() => {
      expect(bankService.getLinkToken).toHaveBeenCalledWith(mockUserId);
    });
  });

  it('handles transaction fetching successfully', async () => {
    const { getByText } = render(
      <BankIntegrationScreen userId={mockUserId} />
    );

    fireEvent.press(getByText('Fetch Transactions'));

    await waitFor(() => {
      expect(bankService.getTransactions).toHaveBeenCalled();
      expect(getByText('Transaction 1')).toBeTruthy();
      expect(getByText('Transaction 2')).toBeTruthy();
    });
  });

  it('handles balance check successfully', async () => {
    const { getByText } = render(
      <BankIntegrationScreen userId={mockUserId} />
    );

    fireEvent.press(getByText('Check Balance'));

    await waitFor(() => {
      expect(bankService.getBalance).toHaveBeenCalledWith(mockUserId);
    });
  });

  it('handles error states appropriately', async () => {
    // Mock error responses
    bankService.getLinkToken.mockRejectedValue(new Error('Connection failed'));
    
    const { getByText, getByPlaceholderText } = render(
      <BankIntegrationScreen userId={mockUserId} />
    );

    fireEvent.changeText(getByPlaceholderText('Enter Bank Name'), 'Test Bank');
    fireEvent.press(getByText('Connect Bank Account'));

    await waitFor(() => {
      expect(getByText('Failed to connect bank account.')).toBeTruthy();
    });
  });

  it('validates bank name input', async () => {
    const { getByText } = render(
      <BankIntegrationScreen userId={mockUserId} />
    );

    fireEvent.press(getByText('Connect Bank Account'));

    await waitFor(() => {
      expect(getByText('Please enter a bank name.')).toBeTruthy();
    });
  });
});
