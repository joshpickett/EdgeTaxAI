import {
  TaxCalculationError,
  IRSComplianceError,
  DeductionValidationError,
  ReportGenerationError,
  ReportValidationError
} from '../errors';

describe('Custom Error Types', () => {
  describe('TaxCalculationError', () => {
    test('should create error with correct properties', () => {
      const error = new TaxCalculationError('Invalid calculation', 'CALC_001');
      expect(error.name).toBe('TaxCalculationError');
      expect(error.message).toBe('Invalid calculation');
      expect(error.code).toBe('CALC_001');
    });
  });

  describe('IRSComplianceError', () => {
    test('should create error with correct properties', () => {
      const error = new IRSComplianceError('Missing documentation', 'IRS_001');
      expect(error.name).toBe('IRSComplianceError');
      expect(error.message).toBe('Missing documentation');
      expect(error.code).toBe('IRS_001');
    });
  });

  describe('DeductionValidationError', () => {
    test('should create error with correct properties', () => {
      const error = new DeductionValidationError('Invalid deduction', 'DED_001');
      expect(error.name).toBe('DeductionValidationError');
      expect(error.message).toBe('Invalid deduction');
      expect(error.code).toBe('DED_001');
    });
  });

  describe('ReportGenerationError', () => {
    test('should create error with correct properties', () => {
      const error = new ReportGenerationError('Generation failed', 'REP_001');
      expect(error.name).toBe('ReportGenerationError');
      expect(error.message).toBe('Generation failed');
      expect(error.code).toBe('REP_001');
    });
  });

  describe('ReportValidationError', () => {
    test('should create error with correct properties', () => {
      const error = new ReportValidationError('Invalid report data', 'VAL_001');
      expect(error.name).toBe('ReportValidationError');
      expect(error.message).toBe('Invalid report data');
      expect(error.code).toBe('VAL_001');
    });
  });
});
