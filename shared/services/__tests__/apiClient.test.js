import { ApiClient } from '../apiClient';
import config from '../../config';
import MockAdapter from 'axios-mock-adapter';

describe('ApiClient', () => {
  let apiClient;
  let mockAxios;

  beforeEach(() => {
    apiClient = new ApiClient();
    mockAxios = new MockAdapter(apiClient.client);
  });

  afterEach(() => {
    mockAxios.restore();
  });

  test('should make successful GET request', async () => {
    const mockData = { data: 'test' };
    mockAxios.onGet('/test').reply(200, mockData);

    const response = await apiClient.get('/test');
    expect(response.data).toEqual(mockData);
  });

  test('should handle network errors', async () => {
    mockAxios.onGet('/test').networkError();
    
    await expect(apiClient.get('/test')).rejects.toThrow('Network Error');
  });

  test('should retry failed requests', async () => {
    mockAxios
      .onGet('/test')
      .replyOnce(500)
      .onGet('/test')
      .replyOnce(200, { data: 'success' });

    const response = await apiClient.get('/test');
    expect(response.data).toEqual({ data: 'success' });
  });

  test('should handle token refresh', async () => {
    const originalToken = 'old-token';
    const newToken = 'new-token';

    mockAxios
      .onGet('/protected')
      .replyOnce(401)
      .onPost('/auth/refresh')
      .replyOnce(200, { token: newToken })
      .onGet('/protected')
      .replyOnce(200, { data: 'protected data' });

    const response = await apiClient.get('/protected');
    expect(response.data).toEqual({ data: 'protected data' });
  });
});
