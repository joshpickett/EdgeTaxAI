import React, { useState } from 'react';
import { FormSection } from './FormSection';
import { FormField } from './FormField';
import { FormValidation } from './FormValidation';

interface ScheduleCProps {
  onSubmit: (data: any) => void;
}

export const ScheduleC: React.FC<ScheduleCProps> = ({ onSubmit }) => {
  const [businessIncome, setBusinessIncome] = useState('');
  const [businessExpenses, setBusinessExpenses] = useState('');
  const [errors, setErrors] = useState<string[]>([]);
  const [isValid, setIsValid] = useState(true);

  const handleBusinessIncomeChange = (value: string) => {
    setBusinessIncome(value);
  };

  const handleBusinessExpensesChange = (value: string) => {
    setBusinessExpenses(value);
  };

  const handleValidation = (valid: boolean, validationErrors: string[]) => {
    setIsValid(valid);
    setErrors(validationErrors);
  };

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    if (isValid) {
      onSubmit({ businessIncome, businessExpenses });
    }
  };

  return (
    <FormSection title="Schedule C: Business Income" description="Report your business income and expenses">
      <form onSubmit={handleSubmit}>
        <FormField
          label="Business Income"
          name="businessIncome"
          value={businessIncome}
          onChange={handleBusinessIncomeChange}
          type="number"
          required
        />
        <FormField
          label="Business Expenses"
          name="businessExpenses"
          value={businessExpenses}
          onChange={handleBusinessExpensesChange}
          type="number"
          required
        />
        <FormValidation
          formType="ScheduleC"
          section="Business Income"
          data={{ businessIncome, businessExpenses }}
          onValidation={handleValidation}
        />
        <button type="submit" disabled={!isValid}>Submit</button>
        {!isValid && errors.length > 0 && (
          <div>
            {errors.map((error, index) => (
              <p key={index} style={{ color: 'red' }}>{error}</p>
            ))}
          </div>
        )}
      </form>
    </FormSection>
  );
};
