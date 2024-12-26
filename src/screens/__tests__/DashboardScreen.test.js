import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import DashboardScreen from '../DashboardScreen';
import { useSelector } from 'react-redux';

jest.mock('react-redux', () => ({
  useSelector: jest.fn(),
  useDispatch: () => jest.fn()
}));

describe('DashboardScreen', () => {
  const mockDashboardData = {
    income: 5000,
    expenses: 3000,
    taxLiability: 1000,
    nextPayment: '2023-06-15'
  };

  beforeEach(() => {
    useSelector.mockImplementation(callback => {
      return callback({ dashboard: mockDashboardData });
    });
  });

  it('renders dashboard data correctly', () => {
    const { getByText } = render(<DashboardScreen />);
    
    expect(getByText('$5,000')).toBeTruthy();
    expect(getByText('$3,000')).toBeTruthy();
    expect(getByText('$1,000')).toBeTruthy();
  });

  it('handles navigation to other screens', () => {
    const mockNavigation = { navigate: jest.fn() };
    const { getByText } = render(<DashboardScreen navigation={mockNavigation} />);
    
    fireEvent.press(getByText('View Expenses'));
    expect(mockNavigation.navigate).toHaveBeenCalledWith('Expenses');
  });

  it('displays loading state', async () => {
    useSelector.mockImplementation(callback => {
      return callback({ dashboard: { loading: true } });
    });

    const { getByTestId } = render(<DashboardScreen />);
    expect(getByTestId('loading-indicator')).toBeTruthy();
  });

  it('handles refresh action', async () => {
    const { getByTestId } = render(<DashboardScreen />);
    
    fireEvent.refresh(getByTestId('dashboard-scroll'));
    await waitFor(() => {
      expect(getByText('$5,000')).toBeTruthy();
    });
  });
});
