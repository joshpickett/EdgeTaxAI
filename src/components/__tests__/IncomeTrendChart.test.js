import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import IncomeTrendChart from '../IncomeTrendChart';

jest.mock('victory-native', () => ({
  VictoryLine: 'VictoryLine',
  VictoryChart: 'VictoryChart',
  VictoryAxis: 'VictoryAxis',
  VictoryTheme: {
    material: 'material'
  }
}));

describe('IncomeTrendChart', () => {
  const mockData = [
    { date: new Date('2023-01-01'), amount: 1000 },
    { date: new Date('2023-02-01'), amount: 1200 },
    { date: new Date('2023-03-01'), amount: 1500 }
  ];

  it('renders chart with data', () => {
    const { getByText, UNSAFE_getByType } = render(
      <IncomeTrendChart data={mockData} />
    );

    expect(getByText('Income Trends')).toBeTruthy();
    expect(UNSAFE_getByType('VictoryLine')).toBeTruthy();
  });

  it('handles period selection', () => {
    const { getByText } = render(<IncomeTrendChart data={mockData} />);

    fireEvent.press(getByText('Quarterly'));
    expect(getByText('Quarterly')).toBeTruthy();

    fireEvent.press(getByText('Yearly'));
    expect(getByText('Yearly')).toBeTruthy();

    fireEvent.press(getByText('Monthly'));
    expect(getByText('Monthly')).toBeTruthy();
  });

  it('applies correct chart dimensions', () => {
    const { UNSAFE_getByType } = render(<IncomeTrendChart data={mockData} />);
    const chart = UNSAFE_getByType('VictoryChart');
    
    expect(chart.props.width).toBeDefined();
    expect(chart.props.height).toBe(250);
  });

  it('formats axis labels correctly', () => {
    const { UNSAFE_getAllByType } = render(<IncomeTrendChart data={mockData} />);
    const axes = UNSAFE_getAllByType('VictoryAxis');
    
    expect(axes).toHaveLength(2);
    expect(axes[1].props.tickFormat).toBeDefined();
  });
});
