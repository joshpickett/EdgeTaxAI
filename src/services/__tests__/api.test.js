import { sendRequest, validateFields, loginUser, signupUser, resetPassword } from '../api';
import { apiClient } from '../apiClient';

jest.mock('../apiClient');

describe('API Service', () => {
  beforeEach(() => {
    fetch.resetMocks();
    apiClient.login.mockClear();
    apiClient.signup.mockClear();
  });

  describe('sendRequest', () => {
    it('handles successful GET requests', async () => {
      const mockResponse = { data: 'test' };
      fetch.mockResponseOnce(JSON.stringify(mockResponse));

      const result = await sendRequest('/test-endpoint');
      expect(result).toEqual(mockResponse);
    });

    it('handles successful POST requests with payload', async () => {
      const mockResponse = { success: true };
      const payload = { test: 'data' };
      fetch.mockResponseOnce(JSON.stringify(mockResponse));

      const result = await sendRequest('/test-endpoint', 'POST', payload);
      expect(result).toEqual(mockResponse);
      expect(fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(payload)
        })
      );
    });

    it('handles API errors', async () => {
      fetch.mockResponseOnce(JSON.stringify({ error: 'Test error' }), { status: 400 });

      await expect(sendRequest('/test-endpoint')).rejects.toThrow('Test error');
    });
  });

  describe('validateFields', () => {
    it('returns true for valid fields', () => {
      const fields = { name: 'Test', email: 'test@test.com' };
      expect(validateFields(fields)).toBe(true);
    });

    it('returns false for invalid fields', () => {
      const fields = { name: '', email: 'test@test.com' };
      expect(validateFields(fields)).toBe(false);
    });
  });

  describe('loginUser', () => {
    it('calls apiClient.login with correct parameters', async () => {
      const credentials = { identifier: 'test@test.com', password: 'password' };
      await loginUser(credentials.identifier, credentials.password);
      expect(apiClient.login).toHaveBeenCalledWith(credentials);
    });
  });

  describe('signupUser', () => {
    it('validates fields before signup', async () => {
      await expect(signupUser('', 'test@test.com', '1234567890', 'password'))
        .rejects.toThrow('All fields are required');
    });

    it('calls apiClient.signup with correct parameters', async () => {
      const userData = {
        full_name: 'Test User',
        email: 'test@test.com',
        phone_number: '1234567890',
        password: 'password'
      };

      await signupUser(
        userData.full_name,
        userData.email,
        userData.phone_number,
        userData.password
      );

      expect(apiClient.signup).toHaveBeenCalledWith(userData);
    });
  });
});
