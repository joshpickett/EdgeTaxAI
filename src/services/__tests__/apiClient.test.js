import { apiClient } from '../apiClient';
import { tokenStorage } from '../../utils/tokenStorage';

jest.mock('../../utils/tokenStorage');

describe('ApiClient', () => {
  beforeEach(() => {
    fetch.mockClear();
    tokenStorage.getToken.mockClear();
  });

  it('adds authorization header when token exists', async () => {
    tokenStorage.getToken.mockReturnValue('test-token');
    fetch.mockResponseOnce(JSON.stringify({ data: 'test' }));

    await apiClient.get('/test');

    expect(fetch).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: 'Bearer test-token'
        })
      })
    );
  });

  it('handles GET requests correctly', async () => {
    const mockResponse = { data: 'test' };
    fetch.mockResponseOnce(JSON.stringify(mockResponse));

    const result = await apiClient.get('/test');
    expect(result).toEqual(mockResponse);
  });

  it('handles POST requests correctly', async () => {
    const mockResponse = { success: true };
    fetch.mockResponseOnce(JSON.stringify(mockResponse));

    const payload = { test: 'data' };
    const result = await apiClient.post('/test', payload);

    expect(fetch).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify(payload)
      })
    );
    expect(result).toEqual(mockResponse);
  });

  it('handles network errors', async () => {
    fetch.mockRejectOnce(new Error('Network error'));

    await expect(apiClient.get('/test')).rejects.toThrow('Network error');
  });

  it('handles API errors', async () => {
    fetch.mockResponseOnce(JSON.stringify({ error: 'API Error' }), { status: 400 });

    await expect(apiClient.get('/test')).rejects.toThrow('API Error');
  });

  it('refreshes token on 401 response', async () => {
    tokenStorage.getToken.mockReturnValue('old-token');
    tokenStorage.getRefreshToken.mockReturnValue('refresh-token');

    fetch
      .mockResponseOnce(JSON.stringify({ error: 'Unauthorized' }), { status: 401 })
      .mockResponseOnce(JSON.stringify({ token: 'new-token' }))
      .mockResponseOnce(JSON.stringify({ data: 'test' }));

    const result = await apiClient.get('/test');

    expect(tokenStorage.setTokens).toHaveBeenCalledWith('new-token');
    expect(result).toEqual({ data: 'test' });
  });
});
