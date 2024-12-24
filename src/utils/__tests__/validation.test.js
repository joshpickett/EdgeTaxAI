import {
  validateEmail,
  validatePhone,
  validatePassword,
  validateAmount,
  validateDescription,
  validateDate
} from '../validation';

describe('Validation Utils', () => {
  describe('validateEmail', () => {
    it('should validate correct email formats', () => {
      expect(validateEmail('test@example.com')).toBeNull();
      expect(validateEmail('test.name@example.co.uk')).toBeNull();
      expect(validateEmail('test+label@example.com')).toBeNull();
    });

    it('should reject invalid email formats', () => {
      expect(validateEmail('')).toBe('Email is required');
      expect(validateEmail('test@')).toBe('Invalid email format');
      expect(validateEmail('test@example')).toBe('Invalid email format');
      expect(validateEmail('@example.com')).toBe('Invalid email format');
      expect(validateEmail('test.example.com')).toBe('Invalid email format');
    });

    it('should handle edge cases', () => {
      expect(validateEmail(null)).toBe('Email is required');
      expect(validateEmail(undefined)).toBe('Email is required');
      expect(validateEmail(' ')).toBe('Invalid email format');
      expect(validateEmail('test@example..com')).toBe('Invalid email format');
    });
  });

  describe('validatePhone', () => {
    it('should validate correct phone formats', () => {
      expect(validatePhone('+1234567890')).toBeNull();
      expect(validatePhone('+442071234567')).toBeNull();
      expect(validatePhone('1234567890')).toBeNull();
    });

    it('should reject invalid phone formats', () => {
      expect(validatePhone('')).toBe('Phone number is required');
      expect(validatePhone('abc')).toBe('Invalid phone number format');
      expect(validatePhone('+abc')).toBe('Invalid phone number format');
      expect(validatePhone('++1234567890')).toBe('Invalid phone number format');
    });

    it('should handle edge cases', () => {
      expect(validatePhone(null)).toBe('Phone number is required');
      expect(validatePhone(undefined)).toBe('Phone number is required');
      expect(validatePhone(' ')).toBe('Invalid phone number format');
      expect(validatePhone('+0123')).toBe('Invalid phone number format');
    });
  });

  describe('validatePassword', () => {
    it('should validate correct password formats', () => {
      expect(validatePassword('password123')).toBeNull();
      expect(validatePassword('longpassword123!@#')).toBeNull();
    });

    it('should reject invalid passwords', () => {
      expect(validatePassword('')).toBe('Password is required');
      expect(validatePassword('short')).toBe('Password must be at least 8 characters');
    });

    it('should handle edge cases', () => {
      expect(validatePassword(null)).toBe('Password is required');
      expect(validatePassword(undefined)).toBe('Password is required');
      expect(validatePassword('       ')).toBeNull(); // Length is valid but might want to add strength check
    });
  });

  describe('validateAmount', () => {
    it('should validate correct amounts', () => {
      expect(validateAmount('100')).toBeNull();
      expect(validateAmount('99.99')).toBeNull();
      expect(validateAmount(100)).toBeNull();
      expect(validateAmount(0.01)).toBeNull();
    });

    it('should reject invalid amounts', () => {
      expect(validateAmount('')).toBe('Amount is required');
      expect(validateAmount('0')).toBe('Amount must be a positive number');
      expect(validateAmount('-100')).toBe('Amount must be a positive number');
    });

    it('should handle edge cases', () => {
      expect(validateAmount(null)).toBe('Amount is required');
      expect(validateAmount(undefined)).toBe('Amount is required');
      expect(validateAmount('abc')).toBe('Amount must be a positive number');
      expect(validateAmount('0.00')).toBe('Amount must be a positive number');
    });
  });

  describe('validateDescription', () => {
    it('should validate correct descriptions', () => {
      expect(validateDescription('Test description')).toBeNull();
      expect(validateDescription('ABC')).toBeNull();
    });

    it('should reject invalid descriptions', () => {
      expect(validateDescription('')).toBe('Description is required');
      expect(validateDescription('ab')).toBe('Description must be at least 3 characters');
    });

    it('should handle edge cases', () => {
      expect(validateDescription(null)).toBe('Description is required');
      expect(validateDescription(undefined)).toBe('Description is required');
      expect(validateDescription('  ')).toBe('Description must be at least 3 characters');
    });
  });

  describe('validateDate', () => {
    it('should validate correct dates', () => {
      expect(validateDate('2023-01-01')).toBeNull();
      expect(validateDate(new Date().toISOString())).toBeNull();
    });

    it('should reject invalid dates', () => {
      expect(validateDate('')).toBe('Date is required');
      expect(validateDate('invalid-date')).toBe('Invalid date format');
      expect(validateDate('2023-13-01')).toBe('Invalid date format');
    });

    it('should handle edge cases', () => {
      expect(validateDate(null)).toBe('Date is required');
      expect(validateDate(undefined)).toBe('Date is required');
      expect(validateDate('0000-00-00')).toBe('Invalid date format');
      expect(validateDate(new Date('invalid'))).toBe('Invalid date format');
    });
  });
});
