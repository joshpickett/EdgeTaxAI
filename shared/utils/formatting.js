import { setupUtilsPath } from './setup_path';
import type { Currency, DateFormat } from '../types/interfaces';

// Initialize utils path
setupUtilsPath();

// Currency formatting options
const currencyOptions = { style: 'currency', currency: 'USD' };

export const formatMileage = (distance: number, unit: 'miles' | 'km' = 'miles'): string => {
  return `${distance.toFixed(1)} ${unit}`;
};

export const formatTaxDeduction = (amount: number): string => {
  return new Intl.NumberFormat('en-US', currencyOptions).format(amount);
};

export const formatDate = (date: string, format: DateFormat = 'short'): string => {
  return new Date(date).toLocaleDateString('en-US', {
    year: format === 'short' ? '2-digit' : 'numeric',
    month: 'short',
    day: 'numeric'
  });
};

export const formatPurpose = (purpose: string): string => {
  return purpose.charAt(0).toUpperCase() + purpose.slice(1).toLowerCase();
};
