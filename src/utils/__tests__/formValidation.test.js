import { validateField, validateForm, commonRules } from '../formValidation';

describe('Form Validation', () => {
  describe('validateField', () => {
    it('should validate required fields', () => {
      const errors = validateField('email', '', { required: true });
      expect(errors).toContain('email is required');
    });

    it('should validate email pattern', () => {
      const validEmail = validateField('email', 'test@example.com', { pattern: 'email' });
      expect(validEmail).toHaveLength(0);

      const invalidEmail = validateField('email', 'invalid-email', { pattern: 'email' });
      expect(invalidEmail).toContain('Please enter a valid email');
    });

    it('should validate minimum length', () => {
      const errors = validateField('password', '123', { minLength: 8 });
      expect(errors).toContain('password must be at least 8 characters');
    });

    it('should validate maximum length', () => {
      const errors = validateField('name', 'a'.repeat(51), { maxLength: 50 });
      expect(errors).toContain('name must not exceed 50 characters');
    });

    it('should handle custom validation rules', () => {
      const customRule = (value) => value !== 'test' ? 'Value must be test' : null;
      const errors = validateField('custom', 'wrong', { custom: customRule });
      expect(errors).toContain('Value must be test');
    });
  });

  describe('validateForm', () => {
    const formData = {
      email: 'test@example.com',
      password: 'password123',
      phone: '+1234567890'
    };

    const rules = {
      email: { required: true, pattern: 'email' },
      password: { required: true, minLength: 8 },
      phone: { required: true, pattern: 'phone' }
    };

    it('should validate valid form data', () => {
      const result = validateForm(formData, rules);
      expect(result.isValid).toBe(true);
      expect(result.errors).toEqual({});
    });

    it('should validate invalid form data', () => {
      const invalidForm = {
        email: 'invalid-email',
        password: '123',
        phone: 'invalid-phone'
      };

      const result = validateForm(invalidForm, rules);
      expect(result.isValid).toBe(false);
      expect(Object.keys(result.errors)).toHaveLength(3);
    });

    it('should handle missing fields', () => {
      const incompleteForm = {
        email: 'test@example.com'
      };

      const result = validateForm(incompleteForm, rules);
      expect(result.isValid).toBe(false);
      expect(result.errors).toHaveProperty('password');
      expect(result.errors).toHaveProperty('phone');
    });
  });

  describe('Common Rules', () => {
    it('should have correct email rules', () => {
      expect(commonRules.email).toEqual({
        required: true,
        pattern: 'email',
        maxLength: 254
      });
    });

    it('should have correct phone rules', () => {
      expect(commonRules.phone).toEqual({
        required: true,
        pattern: 'phone'
      });
    });

    it('should have correct password rules', () => {
      expect(commonRules.password).toEqual({
        required: true,
        minLength: 8,
        maxLength: 128
      });
    });

    it('should have correct amount rules', () => {
      expect(commonRules.amount).toEqual({
        required: true,
        pattern: 'amount'
      });
    });
  });

  describe('Edge Cases', () => {
    it('should handle undefined values', () => {
      const errors = validateField('field', undefined, { required: true });
      expect(errors).toContain('field is required');
    });

    it('should handle null values', () => {
      const errors = validateField('field', null, { required: true });
      expect(errors).toContain('field is required');
    });

    it('should handle empty validation rules', () => {
      const result = validateForm({}, {});
      expect(result.isValid).toBe(true);
      expect(result.errors).toEqual({});
    });

    it('should handle special characters in field values', () => {
      const errors = validateField('email', 'test!@#$%^&*()@example.com', { pattern: 'email' });
      expect(errors).toHaveLength(0);
    });
  });
});
