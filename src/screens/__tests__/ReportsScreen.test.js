import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import ReportsScreen from '../ReportsScreen';
import { reportsService } from '../../services/reportsService';

jest.mock('../../services/reportsService');

describe('ReportsScreen', () => {
  beforeEach(() => {
    reportsService.generateReport.mockClear();
  });

  it('renders reports dashboard correctly', () => {
    const { getByText } = render(<ReportsScreen />);
    
    expect(getByText('Reports Dashboard')).toBeTruthy();
    expect(getByText('IRS-Ready Reports')).toBeTruthy();
    expect(getByText('Custom Reports')).toBeTruthy();
  });

  it('handles IRS report generation', async () => {
    const mockTaxData = { taxLiability: 5000 };
    reportsService.generateReport.mockResolvedValueOnce(mockTaxData);

    const { getByText } = render(<ReportsScreen />);
    
    fireEvent.press(getByText('Fetch IRS Reports'));

    await waitFor(() => {
      expect(reportsService.generateReport).toHaveBeenCalledWith('tax_summary');
      expect(getByText('5000')).toBeTruthy();
    });
  });

  it('handles custom report generation', async () => {
    const mockCustomReports = [
      { date: '2023-01-01', description: 'Test Report', amount: 100 }
    ];
    reportsService.generateReport.mockResolvedValueOnce(mockCustomReports);

    const { getByText, getByPlaceholderText } = render(<ReportsScreen />);
    
    fireEvent.changeText(getByPlaceholderText('Start Date (YYYY-MM-DD)'), '2023-01-01');
    fireEvent.changeText(getByPlaceholderText('End Date (YYYY-MM-DD)'), '2023-12-31');
    fireEvent.press(getByText('Fetch Custom Reports'));

    await waitFor(() => {
      expect(reportsService.generateReport).toHaveBeenCalledWith('custom', {
        startDate: '2023-01-01',
        endDate: '2023-12-31'
      });
      expect(getByText('Test Report')).toBeTruthy();
    });
  });

  it('handles error states', async () => {
    reportsService.generateReport.mockRejectedValueOnce(new Error('Failed to generate report'));

    const { getByText } = render(<ReportsScreen />);
    
    fireEvent.press(getByText('Fetch IRS Reports'));

    await waitFor(() => {
      expect(getByText('Failed to generate report')).toBeTruthy();
    });
  });

  it('validates date inputs for custom reports', async () => {
    const { getByText } = render(<ReportsScreen />);
    
    fireEvent.press(getByText('Fetch Custom Reports'));

    await waitFor(() => {
      expect(getByText('Start Date and End Date are required')).toBeTruthy();
    });
  });
});
