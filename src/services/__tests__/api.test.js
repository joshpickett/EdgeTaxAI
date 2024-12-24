import { sendRequest, validateFields, loginUser, signupUser, resetPassword, addExpense, getExpenses } from '../api';
import { apiClient } from '../apiClient';

// Mock the apiClient
jest.mock('../apiClient');

describe('API Service', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
    global.fetch = jest.fn();
    global.console.error = jest.fn();
    global.console.warn = jest.fn();
  });

  describe('sendRequest', () => {
    it('should make successful GET request', async () => {
      const mockResponse = { ok: true, json: () => Promise.resolve({ data: 'test' }) };
      global.fetch.mockResolvedValueOnce(mockResponse);

      const result = await sendRequest('/test-endpoint');
      expect(result).toEqual({ data: 'test' });
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/test-endpoint'),
        expect.objectContaining({ method: 'GET' })
      );
    });

    it('should make successful POST request with payload', async () => {
      const mockResponse = { ok: true, json: () => Promise.resolve({ data: 'test' }) };
      global.fetch.mockResolvedValueOnce(mockResponse);
      const payload = { test: 'data' };

      await sendRequest('/test-endpoint', 'POST', payload);
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/test-endpoint'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(payload)
        })
      );
    });

    it('should handle API errors', async () => {
      const errorResponse = {
        ok: false,
        json: () => Promise.resolve({ error: 'Test error' })
      };
      global.fetch.mockResolvedValueOnce(errorResponse);

      await expect(sendRequest('/test-endpoint')).rejects.toThrow('Test error');
      expect(console.error).toHaveBeenCalled();
    });

    it('should handle network errors', async () => {
      global.fetch.mockRejectedValueOnce(new Error('Network error'));

      await expect(sendRequest('/test-endpoint')).rejects.toThrow('Network error');
      expect(console.error).toHaveBeenCalled();
    });
  });

  describe('validateFields', () => {
    it('should return true for valid fields', () => {
      const fields = { name: 'John', email: 'john@example.com' };
      expect(validateFields(fields)).toBe(true);
    });

    it('should return false for empty fields', () => {
      const fields = { name: '', email: 'john@example.com' };
      expect(validateFields(fields)).toBe(false);
      expect(console.warn).toHaveBeenCalled();
    });

    it('should return false for null/undefined fields', () => {
      const fields = { name: null, email: undefined };
      expect(validateFields(fields)).toBe(false);
    });
  });

  describe('loginUser', () => {
    it('should call apiClient.login with correct parameters', async () => {
      const credentials = { identifier: 'test@email.com', password: 'password123' };
      apiClient.login.mockResolvedValueOnce({ token: 'test-token' });

      await loginUser(credentials.identifier, credentials.password);
      expect(apiClient.login).toHaveBeenCalledWith(credentials);
    });

    it('should handle login errors', async () => {
      apiClient.login.mockRejectedValueOnce(new Error('Invalid credentials'));
      await expect(loginUser('test@email.com', 'wrong-password'))
        .rejects.toThrow('Invalid credentials');
    });
  });

  describe('signupUser', () => {
    const validUserData = {
      fullName: 'John Doe',
      email: 'john@example.com',
      phoneNumber: '1234567890',
      password: 'password123'
    };

    it('should validate fields before signup', async () => {
      const invalidUserData = { ...validUserData, fullName: '' };
      await expect(signupUser(
        invalidUserData.fullName,
        invalidUserData.email,
        invalidUserData.phoneNumber,
        invalidUserData.password
      )).rejects.toThrow('All fields are required.');
    });

    it('should call apiClient.signup with correct parameters', async () => {
      apiClient.signup.mockResolvedValueOnce({ success: true });
      
      await signupUser(
        validUserData.fullName,
        validUserData.email,
        validUserData.phoneNumber,
        validUserData.password
      );

      expect(apiClient.signup).toHaveBeenCalledWith({
        full_name: validUserData.fullName,
        email: validUserData.email,
        phone_number: validUserData.phoneNumber,
        password: validUserData.password
      });
    });
  });

  describe('resetPassword', () => {
    it('should validate identifier before reset', async () => {
      await expect(resetPassword('')).rejects.toThrow('Email or phone number is required.');
    });

    it('should make reset password request', async () => {
      const mockResponse = { ok: true, json: () => Promise.resolve({ success: true }) };
      global.fetch.mockResolvedValueOnce(mockResponse);

      await resetPassword('test@email.com');
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/auth/password-reset'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ identifier: 'test@email.com' })
        })
      );
    });
  });

  describe('expense operations', () => {
    it('should call apiClient.addExpense for adding expense', async () => {
      const expenseData = { amount: 100, description: 'Test expense' };
      apiClient.addExpense.mockResolvedValueOnce({ id: 1, ...expenseData });

      await addExpense(expenseData);
      expect(apiClient.addExpense).toHaveBeenCalledWith(expenseData);
    });

    it('should call apiClient.getExpenses for fetching expenses', async () => {
      const mockExpenses = [{ id: 1, amount: 100 }];
      apiClient.getExpenses.mockResolvedValueOnce(mockExpenses);

      const result = await getExpenses();
      expect(apiClient.getExpenses).toHaveBeenCalled();
      expect(result).toEqual(mockExpenses);
    });
  });
});
