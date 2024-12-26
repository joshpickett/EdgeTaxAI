import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import TaxReminderScreen from '../TaxReminderScreen';

describe('TaxReminderScreen', () => {
  const mockFetch = jest.fn();
  global.fetch = mockFetch;

  beforeEach(() => {
    mockFetch.mockClear();
  });

  it('renders correctly', () => {
    const { getByText, getByPlaceholderText } = render(<TaxReminderScreen userId="123" />);
    expect(getByText('Set Tax Reminder')).toBeTruthy();
    expect(getByPlaceholderText('Enter Phone Number (+1234567890)')).toBeTruthy();
    expect(getByPlaceholderText('Reminder Date (YYYY-MM-DD)')).toBeTruthy();
  });

  it('handles reminder scheduling', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ success: true })
    });

    const { getByText, getByPlaceholderText } = render(<TaxReminderScreen userId="123" />);
    
    fireEvent.changeText(getByPlaceholderText('Enter Phone Number (+1234567890)'), '+1234567890');
    fireEvent.changeText(getByPlaceholderText('Reminder Date (YYYY-MM-DD)'), '2023-12-31');
    fireEvent.press(getByText('Schedule Reminder'));

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          method: 'POST',
          body: expect.stringContaining('+1234567890')
        })
      );
    });
  });

  it('validates required fields', async () => {
    const { getByText } = render(<TaxReminderScreen userId="123" />);
    
    fireEvent.press(getByText('Schedule Reminder'));

    await waitFor(() => {
      expect(getByText('Both phone number and reminder date are required.')).toBeTruthy();
    });
  });

  it('handles application programming interface errors', async () => {
    mockFetch.mockRejectedValueOnce(new Error('Application programming interface Error'));

    const { getByText, getByPlaceholderText } = render(<TaxReminderScreen userId="123" />);
    
    fireEvent.changeText(getByPlaceholderText('Enter Phone Number (+1234567890)'), '+1234567890');
    fireEvent.changeText(getByPlaceholderText('Reminder Date (YYYY-MM-DD)'), '2023-12-31');
    fireEvent.press(getByText('Schedule Reminder'));

    await waitFor(() => {
      expect(getByText('Failed to schedule tax reminder.')).toBeTruthy();
    });
  });
});
