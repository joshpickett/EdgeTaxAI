import { TripData, MileageRecord, MileageHistory, ApiError } from '../interfaces';

describe('Interface Types', () => {
  describe('TripData', () => {
    test('should validate TripData structure', () => {
      const tripData: TripData = {
        startLocation: '123 Start St',
        endLocation: '456 End Ave',
        purpose: 'Business meeting',
        recurring: false
      };

      expect(tripData).toHaveProperty('startLocation');
      expect(tripData).toHaveProperty('endLocation');
      expect(tripData).toHaveProperty('purpose');
      expect(tripData).toHaveProperty('recurring');
    });
  });

  describe('MileageRecord', () => {
    test('should validate MileageRecord structure', () => {
      const record: MileageRecord = {
        id: 'test-id',
        userId: 'user-123',
        distance: 10.5,
        taxDeduction: 5.25,
        date: '2023-01-01'
      };

      expect(record).toHaveProperty('id');
      expect(record).toHaveProperty('userId');
      expect(record).toHaveProperty('distance');
      expect(record).toHaveProperty('taxDeduction');
      expect(record).toHaveProperty('date');
    });
  });

  describe('MileageHistory', () => {
    test('should validate MileageHistory structure', () => {
      const history: MileageHistory = {
        userId: 'user-123',
        records: [
          {
            id: 'record-1',
            userId: 'user-123',
            distance: 10.5,
            taxDeduction: 5.25,
            date: '2023-01-01'
          }
        ]
      };

      expect(history).toHaveProperty('userId');
      expect(history).toHaveProperty('records');
      expect(Array.isArray(history.records)).toBe(true);
    });
  });

  describe('ApiError', () => {
    test('should validate ApiError structure', () => {
      const error: ApiError = {
        message: 'Test error',
        statusCode: 400
      };

      expect(error).toHaveProperty('message');
      expect(error).toHaveProperty('statusCode');
    });
  });
});
