import { calculateMileage } from '../mileageService';

describe('MileageService', () => {
  beforeEach(() => {
    global.fetch = jest.fn();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('calculateMileage', () => {
    const mockTripData = {
      startLocation: 'Start Point',
      endLocation: 'End Point',
      date: '2023-01-01'
    };

    it('successfully calculates mileage', async () => {
      const mockResponse = {
        distance: 10.5,
        taxDeduction: 5.25
      };

      fetch.mockImplementationOnce(() => 
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockResponse)
        })
      );

      const result = await calculateMileage(mockTripData);
      expect(result).toEqual(mockResponse);
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/mileage'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(mockTripData)
        })
      );
    });

    it('creates expense entry after calculation', async () => {
      const mockMileageResponse = {
        distance: 10.5,
        taxDeduction: 5.25
      };

      fetch
        .mockImplementationOnce(() => 
          Promise.resolve({
            ok: true,
            json: () => Promise.resolve(mockMileageResponse)
          })
        )
        .mockImplementationOnce(() => 
          Promise.resolve({
            ok: true,
            json: () => Promise.resolve({ success: true })
          })
        );

      await calculateMileage(mockTripData);
      
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/expenses'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({
            type: 'mileage',
            ...mockMileageResponse
          })
        })
      );
    });

    it('handles API errors', async () => {
      fetch.mockImplementationOnce(() => 
        Promise.resolve({
          ok: false,
          json: () => Promise.resolve({ error: 'Failed to calculate' })
        })
      );

      await expect(calculateMileage(mockTripData))
        .rejects
        .toThrow('Failed to calculate mileage.');
    });

    it('handles network errors', async () => {
      fetch.mockImplementationOnce(() => 
        Promise.reject(new Error('Network error'))
      );

      await expect(calculateMileage(mockTripData))
        .rejects
        .toThrow('Network error');
    });
  });
});
