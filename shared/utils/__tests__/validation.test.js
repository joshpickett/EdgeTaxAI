import { 
  REPORT_VALIDATION_RULES,
  validateReportData,
  validateTripData,
  validateMileageRecord
} from '../validation';

describe('Report Validation Rules', () => {
  it('should have correct validation rule structure', () => {
    expect(REPORT_VALIDATION_RULES.date).toBeDefined();
    expect(REPORT_VALIDATION_RULES.amount).toBeDefined();
    expect(REPORT_VALIDATION_RULES.category).toBeDefined();
  });
});

describe('validateReportData', () => {
  it('should validate valid report data', () => {
    const validReport = {
      startDate: '2023-01-01',
      endDate: '2023-12-31'
    };
    const result = validateReportData(validReport);
    expect(result.isValid).toBe(true);
    expect(result.errors).toHaveLength(0);
  });

  it('should reject missing dates', () => {
    const invalidReport = {};
    const result = validateReportData(invalidReport);
    expect(result.isValid).toBe(false);
    expect(result.errors).toContain('Date range is required');
  });

  it('should reject invalid date range', () => {
    const invalidReport = {
      startDate: '2023-12-31',
      endDate: '2023-01-01'
    };
    const result = validateReportData(invalidReport);
    expect(result.isValid).toBe(false);
    expect(result.errors).toContain('End date must be after start date');
  });
});

describe('validateTripData', () => {
  it('should validate valid trip data', () => {
    const validTrip = {
      startLocation: 'Start',
      endLocation: 'End',
      purpose: 'Business'
    };
    const result = validateTripData(validTrip);
    expect(result.isValid).toBe(true);
    expect(result.errors).toHaveLength(0);
  });

  it('should reject empty locations', () => {
    const invalidTrip = {
      startLocation: '',
      endLocation: '',
      purpose: 'Business'
    };
    const result = validateTripData(invalidTrip);
    expect(result.isValid).toBe(false);
    expect(result.errors).toContain('Start location is required');
    expect(result.errors).toContain('End location is required');
  });

  it('should reject missing purpose', () => {
    const invalidTrip = {
      startLocation: 'Start',
      endLocation: 'End',
      purpose: ''
    };
    const result = validateTripData(invalidTrip);
    expect(result.isValid).toBe(false);
    expect(result.errors).toContain('Trip purpose is required');
  });
});

describe('validateMileageRecord', () => {
  it('should validate valid mileage record', () => {
    const validRecord = {
      userId: 'user123',
      distance: 10.5,
      date: '2023-01-01'
    };
    const result = validateMileageRecord(validRecord);
    expect(result.isValid).toBe(true);
    expect(result.errors).toHaveLength(0);
  });

  it('should reject missing user ID', () => {
    const invalidRecord = {
      distance: 10.5,
      date: '2023-01-01'
    };
    const result = validateMileageRecord(invalidRecord);
    expect(result.isValid).toBe(false);
    expect(result.errors).toContain('User ID is required');
  });

  it('should reject invalid distance', () => {
    const invalidRecord = {
      userId: 'user123',
      distance: -1,
      date: '2023-01-01'
    };
    const result = validateMileageRecord(invalidRecord);
    expect(result.isValid).toBe(false);
    expect(result.errors).toContain('Valid distance is required');
  });

  it('should reject missing date', () => {
    const invalidRecord = {
      userId: 'user123',
      distance: 10.5
    };
    const result = validateMileageRecord(invalidRecord);
    expect(result.isValid).toBe(false);
    expect(result.errors).toContain('Date is required');
  });
});
