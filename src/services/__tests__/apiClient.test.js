import axios from 'axios';
import { APIClient } from '../apiClient';

// Mock axios
jest.mock('axios');

describe('APIClient', () => {
  let apiClient;
  const mockBaseURL = 'http://test-api.com';
  
  beforeEach(() => {
    // Clear all mocks
    jest.clearAllMocks();
    localStorage.clear();
    
    // Create axios mock instance
    axios.create.mockReturnValue({
      interceptors: {
        request: { use: jest.fn() },
        response: { use: jest.fn() }
      }
    });
    
    apiClient = new APIClient(mockBaseURL);
  });

  describe('Constructor and Setup', () => {
    it('should create axios instance with correct config', () => {
      expect(axios.create).toHaveBeenCalledWith({
        baseURL: mockBaseURL,
        timeout: 10000,
        headers: {
          'Content-Type': 'application/json',
        },
      });
    });

    it('should set up request interceptor', () => {
      const mockToken = 'test-token';
      localStorage.setItem('authToken', mockToken);
      
      // Get the interceptor function
      const interceptorFunction = apiClient.client.interceptors.request.use.mock.calls[0][0];
      
      // Test the interceptor
      const config = { headers: {} };
      const result = interceptorFunction(config);
      
      expect(result.headers.Authorization).toBe(`Bearer ${mockToken}`);
    });

    it('should handle request interceptor error', () => {
      const errorHandler = apiClient.client.interceptors.request.use.mock.calls[0][1];
      const error = new Error('Test error');
      
      expect(() => errorHandler(error)).rejects.toThrow('Test error');
    });
  });

  describe('Error Handling', () => {
    it('should format API errors correctly', () => {
      const error = {
        response: {
          data: { message: 'Test error message' },
          status: 400
        }
      };

      const formattedError = apiClient.handleAPIError(error);
      
      expect(formattedError).rejects.toEqual({
        message: 'Test error message',
        status: 400,
        data: error.response.data
      });
    });

    it('should handle errors without response data', () => {
      const error = {};
      const formattedError = apiClient.handleAPIError(error);
      
      expect(formattedError).rejects.toEqual({
        message: 'An unexpected error occurred',
        status: undefined,
        data: undefined
      });
    });
  });

  describe('Authentication Endpoints', () => {
    it('should handle login request', async () => {
      const credentials = { email: 'test@test.com', password: 'password' };
      const mockResponse = { data: { token: 'test-token' } };
      
      axios.create().post.mockResolvedValueOnce(mockResponse);
      
      await apiClient.login(credentials);
      
      expect(apiClient.client.post).toHaveBeenCalledWith('/auth/login', credentials);
    });

    it('should handle signup request', async () => {
      const userData = { 
        email: 'test@test.com', 
        password: 'password',
        fullName: 'Test User'
      };
      const mockResponse = { data: { user: userData } };
      
      axios.create().post.mockResolvedValueOnce(mockResponse);
      
      await apiClient.signup(userData);
      
      expect(apiClient.client.post).toHaveBeenCalledWith('/auth/signup', userData);
    });

    it('should handle One-Time Password verification', async () => {
      const otpData = { code: '123456', email: 'test@test.com' };
      const mockResponse = { data: { verified: true } };
      
      axios.create().post.mockResolvedValueOnce(mockResponse);
      
      await apiClient.verifyOneTimePassword(otpData);
      
      expect(apiClient.client.post).toHaveBeenCalledWith('/auth/verify-otp', otpData);
    });
  });

  describe('Expense Endpoints', () => {
    it('should handle get expenses request', async () => {
      const params = { page: 1, limit: 10 };
      const mockResponse = { data: { expenses: [] } };
      
      axios.create().get.mockResolvedValueOnce(mockResponse);
      
      await apiClient.getExpenses(params);
      
      expect(apiClient.client.get).toHaveBeenCalledWith('/expenses', { params });
    });

    it('should handle add expense request', async () => {
      const expenseData = { amount: 100, description: 'Test' };
      const mockResponse = { data: { id: 1, ...expenseData } };
      
      axios.create().post.mockResolvedValueOnce(mockResponse);
      
      await apiClient.addExpense(expenseData);
      
      expect(apiClient.client.post).toHaveBeenCalledWith('/expenses', expenseData);
    });

    it('should handle update expense request', async () => {
      const id = 1;
      const expenseData = { amount: 200 };
      const mockResponse = { data: { id, ...expenseData } };
      
      axios.create().put.mockResolvedValueOnce(mockResponse);
      
      await apiClient.updateExpense(id, expenseData);
      
      expect(apiClient.client.put).toHaveBeenCalledWith(`/expenses/${id}`, expenseData);
    });
  });

  describe('Receipt Processing', () => {
    it('should handle receipt processing request', async () => {
      const formData = new FormData();
      const mockResponse = { data: { processed: true } };
      
      axios.create().post.mockResolvedValueOnce(mockResponse);
      
      await apiClient.processReceipt(formData);
      
      expect(apiClient.client.post).toHaveBeenCalledWith(
        '/process-receipt',
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );
    });
  });
});
