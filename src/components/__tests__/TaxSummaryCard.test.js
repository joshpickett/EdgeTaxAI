import React from 'react';
import { render } from '@testing-library/react-native';
import { setupSrcPath } from '../../setup_path';
import TaxSummaryCard from '../TaxSummaryCard';
import { colors, typography } from '../../styles/tokens';

jest.mock('victory-native', () => ({
  VictoryPie: 'VictoryPie'
}));

describe('TaxSummaryCard', () => {
  const mockTaxData = {
    currentQuarter: 2,
    estimatedTax: 5000,
    ytdTaxPaid: 3000,
    nextPaymentDate: '2023-06-15',
    effectiveRate: 25,
    netIncome: 20000
  };

  it('renders tax summary data correctly', () => {
    const { getByText } = render(
      <TaxSummaryCard taxData={mockTaxData} />
    );

    const title = getByText('Quarterly Tax Summary');
    expect(title.props.style).toContainEqual(
      expect.objectContaining({ fontSize: typography.fontSize.xl }));
    expect(getByText('Q2')).toBeTruthy();
    expect(getByText('$5000')).toBeTruthy();
    expect(getByText('$3000')).toBeTruthy();
    expect(getByText('2023-06-15')).toBeTruthy();
    expect(getByText('25%')).toBeTruthy();
  });

  it('renders VictoryPie chart with correct data', () => {
    const { UNSAFE_getByType } = render(
      <TaxSummaryCard taxData={mockTaxData} />
    );

    const pieChart = UNSAFE_getByType('VictoryPie');
    expect(pieChart.props.data).toEqual([
      { x: "Tax", y: mockTaxData.estimatedTax },
      { x: "Net", y: mockTaxData.netIncome }
    ]);
  });

  it('applies correct styles', () => {
    const { getByText } = render(<TaxSummaryCard taxData={mockTaxData} />);
    
    const title = getByText('Quarterly Tax Summary');
    expect(title.parent.props.style).toBeDefined();
  });

  it('handles zero values correctly', () => {
    const zeroTaxData = {
      ...mockTaxData,
      estimatedTax: 0,
      ytdTaxPaid: 0,
      effectiveRate: 0
    };

    const { getByText } = render(<TaxSummaryCard taxData={zeroTaxData} />);
    expect(getByText('$0')).toBeTruthy();
    expect(getByText('0%')).toBeTruthy();
  });
});
