import React from 'react';
import { render } from '@testing-library/react-native';
import DashboardOverview from '../DashboardOverview';
import { dataSyncService } from '../../services/dataSyncService';
import { reportsService } from '../../services/reportsService';

jest.mock('../../services/dataSyncService');
jest.mock('../../services/reportsService');

describe('DashboardOverview', () => {
  const mockData = {
    income: 5000,
    expenses: 3000,
    savings: 2000,
    taxLiability: 1000
  };

  beforeEach(() => {
    dataSyncService.getLatestData.mockResolvedValue(mockData);
    reportsService.generateSummary.mockResolvedValue(mockData);
  });

  it('renders overview data correctly', async () => {
    const { getByText, findByText } = render(<DashboardOverview />);
    
    expect(await findByText('$5,000')).toBeTruthy();
    expect(await findByText('$3,000')).toBeTruthy();
    expect(await findByText('$2,000')).toBeTruthy();
  });

  it('handles loading state', () => {
    dataSyncService.getLatestData.mockImplementation(() => new Promise(() => {}));
    const { getByTestId } = render(<DashboardOverview />);
    expect(getByTestId('loading-indicator')).toBeTruthy();
  });

  it('handles error state', async () => {
    dataSyncService.getLatestData.mockRejectedValue(new Error('Test error'));
    const { findByText } = render(<DashboardOverview />);
    expect(await findByText('Error loading dashboard data')).toBeTruthy();
  });
});
