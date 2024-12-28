import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import { setupSrcPath } from '../../setup_path';
import FinancialPlanningCard from '../FinancialPlanningCard';
import { colors, spacing } from '../../styles/tokens';

jest.mock('victory-native', () => ({
  VictoryPie: 'VictoryPie',
  VictoryBar: 'VictoryBar'
}));

describe('FinancialPlanningCard', () => {
  const mockPlanningData = {
    monthlyGoal: 5000,
    currentMonthly: 3500,
    monthlyProgress: 70,
    recommendedSavings: 1000,
    savingsBreakdown: [
      { x: 'Tax', y: 500 },
      { x: 'Emergency', y: 300 },
      { x: 'General', y: 200 }
    ],
    quarterlyProjections: [
      { quarter: 'Q1', amount: 15000 },
      { quarter: 'Q2', amount: 16000 }
    ],
    onUpdateGoals: jest.fn()
  };

  it('renders financial planning data correctly', () => {
    const { getByText } = render(
      <FinancialPlanningCard planningData={mockPlanningData} />
    );

    expect(getByText('Financial Planning')).toBeTruthy();
    expect(getByText('Monthly Goal: $5000')).toBeTruthy();
    expect(getByText('Progress: $3500 (70%)')).toBeTruthy();
    expect(getByText('Recommended Monthly Savings: $1000')).toBeTruthy();
  });

  it('renders charts correctly', () => {
    const { UNSAFE_getByType } = render(
      <FinancialPlanningCard planningData={mockPlanningData} />
    );

    expect(UNSAFE_getByType('VictoryPie')).toBeTruthy();
    expect(UNSAFE_getByType('VictoryBar')).toBeTruthy();
  });

  it('handles update goals button press', () => {
    const { getByText } = render(
      <FinancialPlanningCard planningData={mockPlanningData} />
    );

    fireEvent.press(getByText('Update Financial Goals'));
    expect(mockPlanningData.onUpdateGoals).toHaveBeenCalled();
  });

  it('displays progress bar correctly', () => {
    const { getByTestId } = render(
      <FinancialPlanningCard planningData={mockPlanningData} />
    );

    const progressBar = getByTestId('progress-bar');
    expect(progressBar.props.style).toContainEqual(expect.objectContaining({ 
      width: '70%',
      backgroundColor: colors.primary.light 
    }));
  });
});
