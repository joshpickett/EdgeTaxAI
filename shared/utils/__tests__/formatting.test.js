import { 
  formatMileage, 
  formatTaxDeduction, 
  formatDate, 
  formatPurpose 
} from '../formatting';

describe('formatMileage', () => {
  it('should format mileage with one decimal place', () => {
    expect(formatMileage(10)).toBe('10.0 miles');
    expect(formatMileage(10.5)).toBe('10.5 miles');
    expect(formatMileage(10.55)).toBe('10.6 miles');
  });

  it('should handle zero mileage', () => {
    expect(formatMileage(0)).toBe('0.0 miles');
  });

  it('should handle large numbers', () => {
    expect(formatMileage(1000.123)).toBe('1000.1 miles');
  });
});

describe('formatTaxDeduction', () => {
  it('should format currency in United States Dollar', () => {
    expect(formatTaxDeduction(1000)).toMatch(/\$1,000\.00/);
    expect(formatTaxDeduction(1234.56)).toMatch(/\$1,234\.56/);
  });

  it('should handle zero amount', () => {
    expect(formatTaxDeduction(0)).toMatch(/\$0\.00/);
  });

  it('should handle large numbers', () => {
    expect(formatTaxDeduction(1000000)).toMatch(/\$1,000,000\.00/);
  });
});

describe('formatDate', () => {
  it('should format dates in short format', () => {
    expect(formatDate('2023-01-01')).toBe('Jan 1, 2023');
    expect(formatDate('2023-12-31')).toBe('Dec 31, 2023');
  });

  it('should handle different date formats', () => {
    expect(formatDate('2023/01/01')).toBe('Jan 1, 2023');
    expect(formatDate('2023-01-01T00:00:00Z')).toBe('Jan 1, 2023');
  });

  it('should throw error for invalid dates', () => {
    expect(() => formatDate('invalid-date')).toThrow();
  });
});

describe('formatPurpose', () => {
  it('should capitalize first letter and lowercase rest', () => {
    expect(formatPurpose('business')).toBe('Business');
    expect(formatPurpose('MEETING')).toBe('Meeting');
    expect(formatPurpose('client VISIT')).toBe('Client visit');
  });

  it('should handle empty strings', () => {
    expect(formatPurpose('')).toBe('');
  });

  it('should handle single character', () => {
    expect(formatPurpose('a')).toBe('A');
  });
});
