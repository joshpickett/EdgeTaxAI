import { apiClient } from '../apiClient';
import MockAdapter from 'axios-mock-adapter';
import { API_ENDPOINTS } from '../../shared/constants';

describe('API Client', () => {
  let mock;

  beforeEach(() => {
    mock = new MockAdapter(apiClient.instance);
  });

  afterEach(() => {
    mock.reset();
  });

  describe('Request Interceptors', () => {
    it('should add authorization header when token exists', async () => {
      localStorage.setItem('auth_token', 'test-token');
      mock.onGet('/test').reply(config => {
        expect(config.headers.Authorization).toBe('Bearer test-token');
        return [200];
      });

      await apiClient.get('/test');
    });

    it('should not add authorization header when token is missing', async () => {
      localStorage.removeItem('auth_token');
      mock.onGet('/test').reply(config => {
        expect(config.headers.Authorization).toBeUndefined();
        return [200];
      });

      await apiClient.get('/test');
    });
  });

  describe('Response Interceptors', () => {
    it('should handle successful responses', async () => {
      const mockData = { success: true };
      mock.onGet('/test').reply(200, mockData);

      const response = await apiClient.get('/test');
      expect(response.data).toEqual(mockData);
    });

    it('should handle unauthorized errors', async () => {
      mock.onGet('/test').reply(401);
      
      await expect(apiClient.get('/test'))
        .rejects.toThrow('Unauthorized');
    });

    it('should handle server errors', async () => {
      mock.onGet('/test').reply(500);
      
      await expect(apiClient.get('/test'))
        .rejects.toThrow('Internal server error');
    });
  });

  describe('Retry Mechanism', () => {
    it('should retry failed requests', async () => {
      let attempts = 0;
      mock.onGet('/test').reply(() => {
        attempts++;
        return attempts < 3 ? [500] : [200, { success: true }];
      });

      const response = await apiClient.get('/test');
      expect(attempts).toBe(3);
      expect(response.data).toEqual({ success: true });
    });
  });
});
