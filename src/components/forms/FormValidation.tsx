import React, { useEffect, useState } from 'react';
import { ValidationFeedback } from './ValidationFeedback';
import { FormValidationService } from 'api/services/form/form_validation_service';

interface FormValidationProps {
  formType: string;
  section: string;
  data: any;
  onValidation: (isValid: boolean, errors: string[]) => void;
}

export const FormValidation: React.FC<FormValidationProps> = ({
  formType,
  section,
  data,
  onValidation
}) => {
  const [validationResult, setValidationResult] = useState<any>(null);
  const validationService = new FormValidationService();

  useEffect(() => {
    validateSection();
  }, [data]);

  const validateSection = async () => {
    try {
      const result = await validationService.validate_section(
        formType,
        section,
        data
      );
      
      setValidationResult(result);
      onValidation(result.is_valid, result.errors);
    } catch (error) {
      console.error('Validation error:', error);
    }
  };

  if (!validationResult) {
    return null;
  }

  return (
    <ValidationFeedback
      errors={validationResult.errors}
      warnings={validationResult.warnings}
      suggestions={validationResult.suggestions}
    />
  );
};
