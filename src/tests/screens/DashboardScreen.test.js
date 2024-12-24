import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import DashboardScreen from '../../screens/DashboardScreen';
import { sharedReportingService } from '../../services/sharedReportingService';

// Mock the sharedReportingService
jest.mock('../../services/sharedReportingService');

describe('DashboardScreen', () => {
  const mockDashboardData = {
    totalExpenses: 1000,
    totalIncome: 2000,
    recentTransactions: [
      { id: 1, description: 'Transaction 1', amount: 100 },
      { id: 2, description: 'Transaction 2', amount: 200 },
    ],
  };

  beforeEach(() => {
    jest.clearAllMocks();
    sharedReportingService.fetchDashboardData.mockResolvedValue(mockDashboardData);
  });

  it('renders loading state initially', () => {
    const { getByTestId } = render(<DashboardScreen />);
    expect(getByTestId('loading-indicator')).toBeTruthy();
  });

  it('renders dashboard data after loading', async () => {
    const { getByText } = render(<DashboardScreen />);
    
    await waitFor(() => {
      expect(getByText('Total Expenses: $1,000')).toBeTruthy();
      expect(getByText('Total Income: $2,000')).toBeTruthy();
    });
  });

  it('handles refresh control correctly', async () => {
    const { getByTestId } = render(<DashboardScreen />);
    
    const scrollView = getByTestId('dashboard-scroll-view');
    fireEvent.scroll(scrollView, {
      nativeEvent: {
        contentOffset: { y: 0 },
        contentSize: { height: 600, width: 400 },
        layoutMeasurement: { height: 400, width: 400 },
      },
    });

    await waitFor(() => {
      expect(sharedReportingService.fetchDashboardData).toHaveBeenCalledTimes(2);
    });
  });

  it('handles error state appropriately', async () => {
    sharedReportingService.fetchDashboardData.mockRejectedValue(
      new Error('Failed to fetch dashboard data')
    );

    const { getByText } = render(<DashboardScreen />);
    
    await waitFor(() => {
      expect(getByText('Error loading dashboard:')).toBeTruthy();
    });
  });

  it('renders empty state when no data is available', async () => {
    sharedReportingService.fetchDashboardData.mockResolvedValue(null);

    const { getByText } = render(<DashboardScreen />);
    
    await waitFor(() => {
      expect(getByText('No dashboard data available')).toBeTruthy();
    });
  });

  it('handles logout functionality', () => {
    const mockOnLogout = jest.fn();
    const { getByText } = render(<DashboardScreen onLogout={mockOnLogout} />);
    
    fireEvent.press(getByText('Logout'));
    expect(mockOnLogout).toHaveBeenCalled();
  });
});
