import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import ReportsScreen from '../../screens/ReportsScreen';
import { sharedReportingService } from '../../services/sharedReportingService';

jest.mock('../../services/sharedReportingService');

describe('ReportsScreen', () => {
  const mockReports = {
    tax_summary: { total: 1000, deductions: 200 },
    custom: [
      { date: '2023-01-01', description: 'Report 1', amount: 100 },
      { date: '2023-01-02', description: 'Report 2', amount: 200 }
    ]
  };

  beforeEach(() => {
    jest.clearAllMocks();
    sharedReportingService.generateReport.mockResolvedValue(mockReports.tax_summary);
  });

  it('renders correctly', () => {
    const { getByText, getByPlaceholderText } = render(<ReportsScreen />);
    expect(getByText('Reports Dashboard')).toBeTruthy();
    expect(getByPlaceholderText('Start Date (YYYY-MM-DD)')).toBeTruthy();
  });

  it('handles Internal Revenue Service report generation', async () => {
    const { getByText } = render(<ReportsScreen />);
    
    fireEvent.press(getByText('Fetch Internal Revenue Service Reports'));
    
    await waitFor(() => {
      expect(sharedReportingService.generateReport).toHaveBeenCalledWith('tax_summary');
      expect(getByText(/Internal Revenue Service Report/)).toBeTruthy();
    });
  });

  it('validates date inputs for custom reports', async () => {
    const { getByText } = render(<ReportsScreen />);
    
    fireEvent.press(getByText('Fetch Custom Reports'));
    
    expect(getByText('Start Date and End Date are required.')).toBeTruthy();
  });

  it('displays custom reports data', async () => {
    sharedReportingService.generateReport.mockResolvedValue(mockReports.custom);
    
    const { getByText, getByPlaceholderText } = render(<ReportsScreen />);
    
    fireEvent.changeText(getByPlaceholderText('Start Date (YYYY-MM-DD)'), '2023-01-01');
    fireEvent.changeText(getByPlaceholderText('End Date (YYYY-MM-DD)'), '2023-01-31');
    fireEvent.press(getByText('Fetch Custom Reports'));

    await waitFor(() => {
      expect(getByText('Report 1')).toBeTruthy();
      expect(getByText('Report 2')).toBeTruthy();
    });
  });

  it('handles empty reports gracefully', async () => {
    sharedReportingService.generateReport.mockResolvedValue([]);
    
    const { getByText, getByPlaceholderText } = render(<ReportsScreen />);
    
    fireEvent.changeText(getByPlaceholderText('Start Date (YYYY-MM-DD)'), '2023-01-01');
    fireEvent.changeText(getByPlaceholderText('End Date (YYYY-MM-DD)'), '2023-01-31');
    fireEvent.press(getByText('Fetch Custom Reports'));

    await waitFor(() => {
      expect(getByText('No custom reports found.')).toBeTruthy();
    });
  });
});
