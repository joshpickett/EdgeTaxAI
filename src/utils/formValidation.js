// Regular expressions for validation
const patterns = {
  email: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  phone: /^\+?[1-9]\d{1,14}$/,
  amount: /^\d+(\.\d{1,2})?$/
};

// Validation rules
export const validateField = (fieldName, value, rules = {}) => {
  const errors = [];

  // Required field validation
  if (rules.required && !value) {
    errors.push(`${fieldName} is required`);
  }

  // Minimum length validation
  if (rules.minLength && value.length < rules.minLength) {
    errors.push(`${fieldName} must be at least ${rules.minLength} characters`);
  }

  // Maximum length validation
  if (rules.maxLength && value.length > rules.maxLength) {
    errors.push(`${fieldName} must not exceed ${rules.maxLength} characters`);
  }

  // Pattern validation
  if (rules.pattern && patterns[rules.pattern]) {
    if (!patterns[rules.pattern].test(value)) {
      errors.push(`Please enter a valid ${fieldName}`);
    }
  }

  // Custom validation
  if (rules.custom && typeof rules.custom === 'function') {
    const customError = rules.custom(value);
    if (customError) {
      errors.push(customError);
    }
  }

  return errors;
};

// Form validation
export const validateForm = (formData, validationRules) => {
  const errors = {};
  
  Object.keys(validationRules).forEach(fieldName => {
    const fieldErrors = validateField(
      fieldName,
      formData[fieldName],
      validationRules[fieldName]
    );
    
    if (fieldErrors.length > 0) {
      errors[fieldName] = fieldErrors;
    }
  });

  return {
    isValid: Object.keys(errors).length === 0,
    errors
  };
};

// Common validation rules
export const commonRules = {
  email: {
    required: true,
    pattern: 'email',
    maxLength: 254
  },
  phone: {
    required: true,
    pattern: 'phone'
  },
  password: {
    required: true,
    minLength: 8,
    maxLength: 128
  },
  amount: {
    required: true,
    pattern: 'amount'
  }
};
