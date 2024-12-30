import { IRSField, IRSValidationResult, IRSComplianceRule } from '../types/irs';
import { IRS_CONSTANTS } from '../constants/irs';

export class IRSValidationService {
  validateField(field: IRSField, value: any): IRSValidationResult {
    const errors = [];
    const warnings = [];

    // Check required fields
    if (field.required && !value) {
      errors.push({
        field: field.id,
        message: IRS_CONSTANTS.ERROR_MESSAGES.REQUIRED_FIELD,
        code: IRS_CONSTANTS.VALIDATION_CODES.REQUIRED_FIELD
      });
    }

    // Check field format
    if (value && field.validation?.pattern) {
      const pattern = new RegExp(field.validation.pattern);
      if (!pattern.test(String(value))) {
        errors.push({
          field: field.id,
          message: field.validation.message || IRS_CONSTANTS.ERROR_MESSAGES.INVALID_FORMAT,
          code: IRS_CONSTANTS.VALIDATION_CODES.INVALID_FORMAT
        });
      }
    }

    // Check range
    if (value && field.validation?.min !== undefined) {
      if (Number(value) < field.validation.min) {
        errors.push({
          field: field.id,
          message: `Value must be at least ${field.validation.min}`,
          code: IRS_CONSTANTS.VALIDATION_CODES.OUT_OF_RANGE
        });
      }
    }

    if (value && field.validation?.max !== undefined) {
      if (Number(value) > field.validation.max) {
        errors.push({
          field: field.id,
          message: `Value must not exceed ${field.validation.max}`,
          code: IRS_CONSTANTS.VALIDATION_CODES.OUT_OF_RANGE
        });
      }
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings
    };
  }

  validateForm(fields: IRSField[], formData: any): IRSValidationResult {
    const errors = [];
    const warnings = [];

    for (const field of fields) {
      const value = formData[field.name];
      const fieldValidation = this.validateField(field, value);
      
      if (!fieldValidation.isValid) {
        errors.push(...fieldValidation.errors);
      }
      if (fieldValidation.warnings) {
        warnings.push(...fieldValidation.warnings);
      }
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings
    };
  }

  validateCompliance(rules: IRSComplianceRule[], data: any): IRSValidationResult {
    const errors = [];
    const warnings = [];

    for (const rule of rules) {
      const value = data[rule.field];
      
      switch (rule.rule) {
        case 'required':
          if (!value) {
            this.addValidationMessage(rule, errors, warnings);
          }
          break;
          
        case 'pattern':
          if (value && !new RegExp(rule.value).test(String(value))) {
            this.addValidationMessage(rule, errors, warnings);
          }
          break;
          
        case 'range':
          if (value && (value < rule.value.min || value > rule.value.max)) {
            this.addValidationMessage(rule, errors, warnings);
          }
          break;
          
        case 'dependency':
          if (value && !data[rule.value]) {
            this.addValidationMessage(rule, errors, warnings);
          }
          break;
      }
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings
    };
  }

  private addValidationMessage(
    rule: IRSComplianceRule,
    errors: any[],
    warnings: any[]
  ) {
    const message = {
      field: rule.field,
      message: rule.message,
      code: IRS_CONSTANTS.VALIDATION_CODES[rule.rule.toUpperCase()]
    };

    if (rule.severity === 'error') {
      errors.push(message);
    } else {
      warnings.push(message);
    }
  }
}

export const irsValidationService = new IRSValidationService();
