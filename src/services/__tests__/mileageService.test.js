import { calculateMileage } from '../mileageService';

describe('MileageService', () => {
  beforeEach(() => {
    global.fetch = jest.fn();
    console.error = jest.fn();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('calculateMileage', () => {
    const mockTripData = {
      startLocation: '123 Start St',
      endLocation: '456 End Ave',
      date: '2023-01-01',
      purpose: 'Business meeting'
    };

    it('should calculate mileage and create expense successfully', async () => {
      const mockMileageResponse = {
        distance: 50,
        rate: 0.65,
        total: 32.50
      };

      // Mock successful mileage calculation
      global.fetch.mockImplementationOnce(() => 
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockMileageResponse)
        })
      );

      // Mock successful expense creation
      global.fetch.mockImplementationOnce(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ id: 1, ...mockMileageResponse })
        })
      );

      const result = await calculateMileage(mockTripData);
      
      expect(result).toEqual(mockMileageResponse);
      expect(global.fetch).toHaveBeenCalledTimes(2);
      expect(global.fetch).toHaveBeenNthCalledWith(1, 
        'https://your-backend-api.com/api/mileage',
        expect.any(Object)
      );
      expect(global.fetch).toHaveBeenNthCalledWith(2,
        'https://your-backend-api.com/api/expenses',
        expect.any(Object)
      );
    });

    it('should handle mileage calculation error', async () => {
      global.fetch.mockImplementationOnce(() =>
        Promise.resolve({
          ok: false,
          json: () => Promise.resolve({ error: 'Invalid locations' })
        })
      );

      await expect(calculateMileage(mockTripData))
        .rejects.toThrow('Invalid locations');
      expect(console.error).toHaveBeenCalled();
    });

    it('should handle network errors', async () => {
      global.fetch.mockImplementationOnce(() =>
        Promise.reject(new Error('Network error'))
      );

      await expect(calculateMileage(mockTripData))
        .rejects.toThrow('Network error');
      expect(console.error).toHaveBeenCalled();
    });

    it('should handle expense creation error', async () => {
      // Mock successful mileage calculation
      global.fetch.mockImplementationOnce(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ distance: 50, rate: 0.65, total: 32.50 })
        })
      );

      // Mock failed expense creation
      global.fetch.mockImplementationOnce(() =>
        Promise.resolve({
          ok: false,
          json: () => Promise.resolve({ error: 'Failed to create expense' })
        })
      );

      const result = await calculateMileage(mockTripData);
      expect(result).toEqual({ distance: 50, rate: 0.65, total: 32.50 });
      expect(console.error).toHaveBeenCalled();
    });

    it('should validate required trip data', async () => {
      const invalidTripData = {
        startLocation: '',
        endLocation: '456 End Ave'
      };

      await expect(calculateMileage(invalidTripData))
        .rejects.toThrow();
    });

    it('should handle zero distance trips', async () => {
      const sameLocationTrip = {
        startLocation: '123 Same St',
        endLocation: '123 Same St',
        date: '2023-01-01'
      };

      global.fetch.mockImplementationOnce(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ distance: 0, rate: 0.65, total: 0 })
        })
      );

      const result = await calculateMileage(sameLocationTrip);
      expect(result.total).toBe(0);
    });

    it('should handle maximum distance limits', async () => {
      const longDistanceTrip = {
        startLocation: 'New York',
        endLocation: 'Los Angeles',
        date: '2023-01-01'
      };

      global.fetch.mockImplementationOnce(() =>
        Promise.resolve({
          ok: false,
          json: () => Promise.resolve({ error: 'Distance exceeds maximum limit' })
        })
      );

      await expect(calculateMileage(longDistanceTrip))
        .rejects.toThrow('Distance exceeds maximum limit');
    });
  });
});
