import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import { Alert } from 'react-native';
import TaxReminderScreen from '../../screens/TaxReminderScreen';

// Mock fetch
global.fetch = jest.fn();

describe('TaxReminderScreen', () => {
  const mockUserId = '123';

  beforeEach(() => {
    jest.clearAllMocks();
    fetch.mockImplementation(() => 
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ success: true })
      })
    );
  });

  it('renders correctly', () => {
    const { getByText, getByPlaceholderText } = render(
      <TaxReminderScreen userId={mockUserId} />
    );
    
    expect(getByText('Set Tax Reminder')).toBeTruthy();
    expect(getByPlaceholderText('Enter Phone Number (+1234567890)')).toBeTruthy();
    expect(getByPlaceholderText('Reminder Date (YYYY-MM-DD)')).toBeTruthy();
  });

  it('validates required fields', async () => {
    const { getByText } = render(<TaxReminderScreen userId={mockUserId} />);
    
    fireEvent.press(getByText('Schedule Reminder'));

    await waitFor(() => {
      expect(Alert.alert).toHaveBeenCalledWith(
        'Error',
        'Both phone number and reminder date are required.'
      );
    });
  });

  it('handles successful reminder creation', async () => {
    const { getByText, getByPlaceholderText } = render(
      <TaxReminderScreen userId={mockUserId} />
    );
    
    fireEvent.changeText(
      getByPlaceholderText('Enter Phone Number (+1234567890)'),
      '+1234567890'
    );
    fireEvent.changeText(
      getByPlaceholderText('Reminder Date (YYYY-MM-DD)'),
      '2024-04-15'
    );
    fireEvent.press(getByText('Schedule Reminder'));

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        'https://your-backend-api.com/api/tax/reminders',
        expect.any(Object)
      );
      expect(Alert.alert).toHaveBeenCalledWith(
        'Success',
        'Tax reminder scheduled successfully!'
      );
    });
  });

  it('handles API errors', async () => {
    fetch.mockImplementationOnce(() => 
      Promise.resolve({
        ok: false,
        json: () => Promise.resolve({ error: 'API Error' })
      })
    );

    const { getByText, getByPlaceholderText } = render(
      <TaxReminderScreen userId={mockUserId} />
    );
    
    fireEvent.changeText(
      getByPlaceholderText('Enter Phone Number (+1234567890)'),
      '+1234567890'
    );
    fireEvent.changeText(
      getByPlaceholderText('Reminder Date (YYYY-MM-DD)'),
      '2024-04-15'
    );
    fireEvent.press(getByText('Schedule Reminder'));

    await waitFor(() => {
      expect(Alert.alert).toHaveBeenCalledWith(
        'Error',
        'Failed to schedule tax reminder.'
      );
    });
  });

  it('validates phone number format', async () => {
    const { getByText, getByPlaceholderText } = render(
      <TaxReminderScreen userId={mockUserId} />
    );
    
    fireEvent.changeText(
      getByPlaceholderText('Enter Phone Number (+1234567890)'),
      'invalid'
    );
    fireEvent.changeText(
      getByPlaceholderText('Reminder Date (YYYY-MM-DD)'),
      '2024-04-15'
    );
    fireEvent.press(getByText('Schedule Reminder'));

    await waitFor(() => {
      expect(Alert.alert).toHaveBeenCalledWith(
        'Error',
        expect.stringContaining('phone')
      );
    });
  });

  it('validates date format', async () => {
    const { getByText, getByPlaceholderText } = render(
      <TaxReminderScreen userId={mockUserId} />
    );
    
    fireEvent.changeText(
      getByPlaceholderText('Enter Phone Number (+1234567890)'),
      '+1234567890'
    );
    fireEvent.changeText(
      getByPlaceholderText('Reminder Date (YYYY-MM-DD)'),
      'invalid-date'
    );
    fireEvent.press(getByText('Schedule Reminder'));

    await waitFor(() => {
      expect(Alert.alert).toHaveBeenCalledWith(
        'Error',
        expect.stringContaining('date')
      );
    });
  });
});
