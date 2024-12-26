import MileageService from '../mileageService';
import { apiClient } from '../apiClient';
import { handleApiError } from '../../utils/errorHandler';
import config from '../../config';

jest.mock('../apiClient');
jest.mock('../../utils/errorHandler');

describe('MileageService', () => {
    beforeEach(() => {
        jest.clearAllMocks();
        global.navigator.onLine = true;
    });

    describe('calculateMileage', () => {
        const mockTripData = {
            startLocation: '123 Start St',
            endLocation: '456 End St',
            date: '2023-01-01',
            purpose: 'Business Meeting'
        };

        test('should calculate mileage online successfully', async () => {
            apiClient.post.mockResolvedValueOnce({
                data: {
                    distance: 10.5,
                    tax_deduction: 6.3
                }
            });

            const result = await MileageService.calculateMileage(mockTripData);
            expect(result.distance).toBe(10.5);
            expect(result.tax_deduction).toBe(6.3);
        });

        test('should handle offline calculation', async () => {
            global.navigator.onLine = false;
            const result = await MileageService.calculateMileage(mockTripData);
            expect(result.distance).toBe("Offline calculation not available");
            expect(result.tax_deduction).toBe(0);
        });

        test('should handle API errors', async () => {
            const error = new Error('API Error');
            apiClient.post.mockRejectedValueOnce(error);
            handleApiError.mockImplementationOnce(err => { throw err; });

            await expect(
                MileageService.calculateMileage(mockTripData)
            ).rejects.toThrow('API Error');
        });
    });

    describe('addMileageRecord', () => {
        const mockRecord = {
            userId: '123',
            distance: 10.5,
            date: '2023-01-01',
            purpose: 'Business'
        };

        test('should add mileage record successfully', async () => {
            apiClient.post.mockResolvedValueOnce({
                data: { id: 'record1', ...mockRecord }
            });

            const result = await MileageService.addMileageRecord(mockRecord);
            expect(result.id).toBe('record1');
        });

        test('should handle record addition errors', async () => {
            apiClient.post.mockRejectedValueOnce(new Error('Failed to add record'));
            handleApiError.mockImplementationOnce(err => { throw err; });

            await expect(
                MileageService.addMileageRecord(mockRecord)
            ).rejects.toThrow('Failed to add record');
        });
    });

    describe('getMileageHistory', () => {
        test('should fetch mileage history successfully', async () => {
            const mockHistory = [
                { id: 1, distance: 10.5 },
                { id: 2, distance: 15.2 }
            ];

            apiClient.get.mockResolvedValueOnce({
                data: mockHistory
            });

            const result = await MileageService.getMileageHistory('user123');
            expect(result).toEqual(mockHistory);
            expect(apiClient.get).toHaveBeenCalledWith(
                '/mileage/history',
                expect.any(Object)
            );
        });

        test('should handle history fetch errors', async () => {
            apiClient.get.mockRejectedValueOnce(new Error('Failed to fetch history'));
            handleApiError.mockImplementationOnce(err => { throw err; });

            await expect(
                MileageService.getMileageHistory('user123')
            ).rejects.toThrow('Failed to fetch history');
        });
    });
});
