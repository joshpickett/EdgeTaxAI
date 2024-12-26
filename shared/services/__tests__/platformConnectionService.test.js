import PlatformConnectionService from '../platformConnectionService';
import { apiClient } from '../apiClient';
import { handleApiError } from '../../utils/errorHandler';
import { PLATFORMS } from '../../constants';

jest.mock('../apiClient');
jest.mock('../../utils/errorHandler');

describe('PlatformConnectionService', () => {
    beforeEach(() => {
        jest.clearAllMocks();
    });

    describe('connectPlatform', () => {
        const userId = '123';
        const platform = 'uber';

        test('should connect platform successfully', async () => {
            const mockResponse = {
                data: {
                    status: 'connected',
                    platformId: 'uber-123'
                }
            };
            apiClient.post.mockResolvedValueOnce(mockResponse);

            const result = await PlatformConnectionService.connectPlatform(platform, userId);
            expect(result).toEqual(mockResponse.data);
            expect(apiClient.post).toHaveBeenCalledWith(
                `/platforms/${platform}/connect`,
                { userId }
            );
        });

        test('should handle connection errors', async () => {
            const error = new Error('Connection failed');
            apiClient.post.mockRejectedValueOnce(error);
            handleApiError.mockImplementationOnce(err => { throw err; });

            await expect(
                PlatformConnectionService.connectPlatform(platform, userId)
            ).rejects.toThrow('Connection failed');
        });
    });

    describe('disconnectPlatform', () => {
        test('should disconnect platform successfully', async () => {
            apiClient.post.mockResolvedValueOnce({
                data: { status: 'disconnected' }
            });

            const result = await PlatformConnectionService.disconnectPlatform('lyft', '123');
            expect(result).toEqual({ status: 'disconnected' });
        });

        test('should handle disconnection errors', async () => {
            apiClient.post.mockRejectedValueOnce(new Error('Disconnection failed'));
            handleApiError.mockImplementationOnce(err => { throw err; });

            await expect(
                PlatformConnectionService.disconnectPlatform('lyft', '123')
            ).rejects.toThrow('Disconnection failed');
        });
    });

    describe('getConnectedPlatforms', () => {
        test('should fetch connected platforms successfully', async () => {
            const mockPlatforms = [
                { platform: 'uber', status: 'active' },
                { platform: 'lyft', status: 'active' }
            ];
            apiClient.get.mockResolvedValueOnce({ data: mockPlatforms });

            const result = await PlatformConnectionService.getConnectedPlatforms('123');
            expect(result).toEqual(mockPlatforms);
        });

        test('should handle fetch errors', async () => {
            apiClient.get.mockRejectedValueOnce(new Error('Fetch failed'));
            handleApiError.mockImplementationOnce(err => { throw err; });

            await expect(
                PlatformConnectionService.getConnectedPlatforms('123')
            ).rejects.toThrow('Fetch failed');
        });
    });

    describe('validateConnection', () => {
        test('should validate connection successfully', async () => {
            apiClient.get.mockResolvedValueOnce({
                data: { isValid: true, lastSync: new Date().toISOString() }
            });

            const result = await PlatformConnectionService.validateConnection('uber', '123');
            expect(result.isValid).toBe(true);
        });

        test('should handle validation errors', async () => {
            apiClient.get.mockRejectedValueOnce(new Error('Validation failed'));
            handleApiError.mockImplementationOnce(err => { throw err; });

            await expect(
                PlatformConnectionService.validateConnection('uber', '123')
            ).rejects.toThrow('Validation failed');
        });
    });
});
