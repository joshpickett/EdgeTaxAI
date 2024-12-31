import React from 'react';
import { FormSection } from './FormSection';
import { FormField } from './FormField';
import { FormValidation } from './FormValidation';

interface ScheduleBProps {
  data: {
    interestIncome: string;
    dividendIncome: string;
  };
  onChange: (field: string, value: string) => void;
  onValidation: (isValid: boolean, errors: string[]) => void;
}

export const ScheduleB: React.FC<ScheduleBProps> = ({
  data,
  onChange,
  onValidation
}) => {
  const handleInterestChange = (value: string) => {
    onChange('interestIncome', value);
  };

  const handleDividendChange = (value: string) => {
    onChange('dividendIncome', value);
  };

  return (
    <FormSection title="Schedule B: Interest and Dividends">
      <FormField
        label="Interest Income"
        name="interestIncome"
        value={data.interestIncome}
        onChange={handleInterestChange}
        type="number"
        required
      />
      <FormField
        label="Dividend Income"
        name="dividendIncome"
        value={data.dividendIncome}
        onChange={handleDividendChange}
        type="number"
        required
      />
      <FormValidation
        formType="ScheduleB"
        section="Interest and Dividends"
        data={data}
        onValidation={onValidation}
      />
    </FormSection>
};
