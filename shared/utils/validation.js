import { setupUtilsPath } from './setup_path';
import { TripData, MileageRecord } from '../types/interfaces';

setupUtilsPath();

// Report validation rules
export const REPORT_VALIDATION_RULES = {
  date: {
    required: true,
    format: 'YYYY-MM-DD'
  },
  amount: {
    required: true,
    min: 0
  },
  category: {
    required: true,
    allowedValues: ['business', 'personal', 'mixed'],
    validateFormat: true
  }
};

export const validateReportData = (reportData) => {
  const errors = [];
  
  if (!reportData.startDate || !reportData.endDate) {
    errors.push('Date range is required');
  }
  
  if (reportData.endDate < reportData.startDate) {
    errors.push('End date must be after start date');
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
};

export const validateTripData = (tripData: TripData) => {
  const errors = [];
  
  if (!tripData.startLocation?.trim()) {
    errors.push('Start location is required');
  }
  
  if (!tripData.endLocation?.trim()) {
    errors.push('End location is required');
  }
  
  if (!tripData.purpose?.trim()) {
    errors.push('Trip purpose is required');
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
};

export const validateMileageRecord = (record: MileageRecord): ValidationResult => {
  const errors = [];
  
  if (!record.userId) {
    errors.push('User ID is required');
  }
  
  if (typeof record.distance !== 'number' || record.distance <= 0) {
    errors.push('Valid distance is required');
  }
  
  if (!record.date) {
    errors.push('Date is required');
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
};
