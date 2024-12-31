import React from 'react';
import { FormSection } from './FormSection';
import { FormField } from './FormField';
import { FormValidation } from './FormValidation';

const ScheduleA: React.FC = () => {
  const [formData, setFormData] = React.useState({
    deduction1: '',
    deduction2: '',
  });

  const [isValid, setIsValid] = React.useState(true);
  const [errors, setErrors] = React.useState<string[]>([]);

  const handleChange = (name: string) => (value: string) => {
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleValidation = (valid: boolean, validationErrors: string[]) => {
    setIsValid(valid);
    setErrors(validationErrors);
  };

  return (
    <FormSection title="Schedule A: Itemized Deductions" description="Please enter your itemized deductions.">
      <FormField
        label="Deduction 1"
        name="deduction1"
        value={formData.deduction1}
        onChange={handleChange('deduction1')}
        type="number"
        required
        error={errors.find(error => error.includes('Deduction 1'))}
      />
      <FormField
        label="Deduction 2"
        name="deduction2"
        value={formData.deduction2}
        onChange={handleChange('deduction2')}
        type="number"
        required
        error={errors.find(error => error.includes('Deduction 2'))}
      />
      <FormValidation
        formType="ScheduleA"
        section="Itemized Deductions"
        data={formData}
        onValidation={handleValidation}
      />
    </FormSection>
  );
};

export default ScheduleA;
