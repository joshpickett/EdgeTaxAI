import PlatformService from '../platformService';
import ApiClient from '../apiClient';
import { PLATFORMS } from '../../constants';
import { handleApiError } from '../../utils/errorHandler';

jest.mock('../apiClient');
jest.mock('../../utils/errorHandler');

describe('PlatformService', () => {
    let platformService;

    beforeEach(() => {
        platformService = new PlatformService();
        jest.clearAllMocks();
    });

    describe('connectPlatform', () => {
        const userId = '123';
        const platform = 'uber';

        test('should connect platform successfully', async () => {
            const mockResponse = { data: { status: 'connected' } };
            ApiClient.post.mockResolvedValueOnce(mockResponse);

            const result = await platformService.connectPlatform(platform, userId);
            expect(result).toEqual(mockResponse.data);
            expect(ApiClient.post).toHaveBeenCalledWith(
                `/platforms/connect/${platform}`,
                { userId, platform }
            );
        });

        test('should handle connection errors', async () => {
            const error = new Error('Connection failed');
            ApiClient.post.mockRejectedValueOnce(error);
            handleApiError.mockImplementationOnce(err => { throw err; });

            await expect(
                platformService.connectPlatform(platform, userId)
            ).rejects.toThrow('Connection failed');
        });
    });

    describe('syncAllPlatforms', () => {
        test('should sync all platforms successfully', async () => {
            const userId = '123';
            ApiClient.post.mockResolvedValue({ data: { status: 'synced' } });

            const result = await platformService.syncAllPlatforms(userId);
            expect(result).toBe(true);
            expect(ApiClient.post).toHaveBeenCalledTimes(Object.keys(PLATFORMS).length);
        });

        test('should not start new sync if sync in progress', async () => {
            platformService.syncInProgress = true;
            const result = await platformService.syncAllPlatforms('123');
            expect(result).toBeUndefined();
            expect(ApiClient.post).not.toHaveBeenCalled();
        });
    });

    describe('getPlatformStatus', () => {
        test('should get platform status successfully', async () => {
            ApiClient.get.mockResolvedValueOnce({
                data: { status: 'active' }
            });

            const result = await platformService.getPlatformStatus('uber', '123');
            expect(result).toEqual({ status: 'active' });
        });
    });
});
