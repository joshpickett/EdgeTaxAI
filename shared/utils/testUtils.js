import { setupUtilsPath } from './setup_path';
import { TripData, MileageRecord } from '../types/interfaces';

setupUtilsPath();

export const mockTripData: TripData = {
  startLocation: '123 Start St',
  endLocation: '456 End Ave',
  purpose: 'Business meeting',
  recurring: false
};

export const mockMileageRecord: MileageRecord = {
  id: 'test-id',
  userId: 'test-user',
  distance: 10.5,
  taxDeduction: 6.87,
  date: '2023-01-01',
  status: 'pending'
};

export const createMockTripData = (overrides = {}): TripData => ({
  ...mockTripData,
  ...overrides
});

export const createMockMileageRecord = (overrides = {}): MileageRecord => ({
  ...mockMileageRecord,
  ...overrides
});
