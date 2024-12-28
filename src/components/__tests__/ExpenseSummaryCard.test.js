import React from 'react';
import { render } from '@testing-library/react-native';
import { setupSrcPath } from '../../setup_path';
import ExpenseSummaryCard from '../ExpenseSummaryCard';
import { colors, typography } from '../../styles/tokens';

jest.mock('victory-native', () => ({
  VictoryPie: 'VictoryPie'
}));

describe('ExpenseSummaryCard', () => {
  const mockData = {
    expenses: [],
    categories: [
      { name: 'Food', amount: 100 },
      { name: 'Transport', amount: 50 },
      { name: 'Entertainment', amount: 30 }
    ],
    total: 180
  };

  it('renders expense summary correctly', () => {
    const { getByText } = render(<ExpenseSummaryCard data={mockData} />);
    
    expect(getByText('Expense Summary')).toBeTruthy();
    expect(getByText('Total Expenses:')).toBeTruthy();
    expect(getByText('$180')).toBeTruthy();
  });

  it('displays top categories', () => {
    const { getByText } = render(<ExpenseSummaryCard data={mockData} />);
    
    expect(getByText('Food: $100')).toBeTruthy();
    expect(getByText('Transport: $50')).toBeTruthy();
    expect(getByText('Entertainment: $30')).toBeTruthy();
  });

  it('renders amount correctly', () => {
    const { getByText } = render(<ExpenseSummaryCard data={mockData} />);
    const amountElement = getByText('$180');
    expect(amountElement.props.style).toContainEqual(
      expect.objectContaining({ color: colors.text.primary })
    );
  });

  it('renders pie chart', () => {
    const { UNSAFE_getByType } = render(<ExpenseSummaryCard data={mockData} />);
    expect(UNSAFE_getByType('VictoryPie')).toBeTruthy();
  });
});
