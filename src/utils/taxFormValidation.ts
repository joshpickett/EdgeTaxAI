import { Form1040Data } from 'shared/types/form1040';
import { TAX_WIZARD_CONFIG } from '../config/taxWizardConfig';

export interface ValidationResult {
  isValid: boolean;
  errors: Record<string, string>;
}

export class TaxFormValidator {
  static validateStep(stepId: string, formData: Partial<Form1040Data>): ValidationResult {
    const stepConfig = TAX_WIZARD_CONFIG.steps[stepId];
    const errors: Record<string, string> = {};

    if (!stepConfig?.validation) {
      return { isValid: true, errors: {} };
    }

    for (const field of stepConfig.validation) {
      const value = this.getNestedValue(formData, field);
      const validationRule = TAX_WIZARD_CONFIG.validation[field];

      if (validationRule) {
        if (validationRule.pattern && !validationRule.pattern.test(String(value))) {
          errors[field] = validationRule.message;
        }
      } else if (!value && stepConfig.required) {
        errors[field] = `${field} is required`;
      }
    }

    return {
      isValid: Object.keys(errors).length === 0,
      errors
    };
  }

  static validateForm(formData: Partial<Form1040Data>): ValidationResult {
    const errors: Record<string, string> = {};

    // Validate all required steps
    Object.entries(TAX_WIZARD_CONFIG.steps)
      .filter(([_, config]) => config.required)
      .forEach(([stepId, _]) => {
        const stepValidation = this.validateStep(stepId, formData);
        Object.assign(errors, stepValidation.errors);
      });

    return {
      isValid: Object.keys(errors).length === 0,
      errors
    };
  }

  private static getNestedValue(obj: any, path: string): any {
    return path.split('.').reduce((current, key) => 
      current && current[key] !== undefined ? current[key] : undefined, obj);
  }
}
