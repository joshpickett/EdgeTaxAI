import React from 'react';
import { FormSection } from './FormSection';
import { FormField } from './FormField';
import { FormValidation } from './FormValidation';

const ScheduleD: React.FC = () => {
  const [formData, setFormData] = React.useState({
    capitalGains: '',
    otherIncome: ''
  });

  const [validationErrors, setValidationErrors] = React.useState<string[]>([]);

  const handleChange = (name: string) => (value: string) => {
    setFormData({
      ...formData,
      [name]: value
    });
  };

  const handleValidation = (isValid: boolean, errors: string[]) => {
    if (!isValid) {
      setValidationErrors(errors);
    } else {
      setValidationErrors([]);
    }
  };

  return (
    <FormSection title="Schedule D: Capital Gains">
      <FormField
        label="Capital Gains"
        name="capitalGains"
        value={formData.capitalGains}
        onChange={handleChange('capitalGains')}
        type="number"
        required
        error={validationErrors.find(error => error.includes('Capital Gains'))}
      />
      <FormField
        label="Other Income"
        name="otherIncome"
        value={formData.otherIncome}
        onChange={handleChange('otherIncome')}
        type="number"
        required
        error={validationErrors.find(error => error.includes('Other Income'))}
      />
      <FormValidation
        formType="ScheduleD"
        section="Capital Gains"
        data={formData}
        onValidation={handleValidation}
      />
    </FormSection>
  );
};

export default ScheduleD;
