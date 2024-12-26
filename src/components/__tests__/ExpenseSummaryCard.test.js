import React from 'react';
import { render } from '@testing-library/react-native';
import ExpenseSummaryCard from '../ExpenseSummaryCard';
import ErrorMessage from '../ErrorMessage';

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

  it('renders pie chart', () => {
    const { UNSAFE_getByType } = render(<ExpenseSummaryCard data={mockData} />);
    expect(UNSAFE_getByType('VictoryPie')).toBeTruthy();
  });
});
