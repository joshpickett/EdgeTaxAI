import React from 'react';
import { FormSection } from './FormSection';
import { FormField } from './FormField';

interface ScheduleFProps {
  farmIncome: number;
  onFarmIncomeChange: (value: number) => void;
  errors?: string[];
}

export const ScheduleF: React.FC<ScheduleFProps> = ({
  farmIncome,
  onFarmIncomeChange,
  errors = []
}) => {
  return (
    <FormSection title="Schedule F: Farm Income" errors={errors}>
      <FormField
        label="Farm Income"
        name="farmIncome"
        value={farmIncome.toString()}
        onChange={(value) => onFarmIncomeChange(Number(value))}
        type="number"
        required
        placeholder="Enter your farm income"
      />
    </FormSection>
  );
};
