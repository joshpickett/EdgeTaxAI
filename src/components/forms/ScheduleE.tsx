import React from 'react';
import { FormSection } from './FormSection';
import { FormField } from './FormField';
import { FormValidation } from './FormValidation';

interface ScheduleEProps {
  rentalIncome: number;
  onChange: (value: number) => void;
  onValidation: (isValid: boolean, errors: string[]) => void;
}

export const ScheduleE: React.FC<ScheduleEProps> = ({
  rentalIncome,
  onChange,
  onValidation
}) => {
  const handleRentalIncomeChange = (value: string) => {
    onChange(Number(value));
  };

  return (
    <FormSection title="Schedule E: Rental Income">
      <FormField
        label="Rental Income"
        name="rentalIncome"
        value={rentalIncome.toString()}
        onChange={handleRentalIncomeChange}
        type="number"
        required
        placeholder="Enter rental income"
      />
      <FormValidation
        formType="ScheduleE"
        section="Rental Income"
        data={{ rentalIncome }}
        onValidation={onValidation}
      />
    </FormSection>
  );
};
