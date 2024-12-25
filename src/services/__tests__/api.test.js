import { api } from '../api';
import MockAdapter from 'axios-mock-adapter';
import { API_ENDPOINTS } from '../../shared/constants';

describe('API Service', () => {
  let mock;

  beforeEach(() => {
    mock = new MockAdapter(api.client);
  });

  afterEach(() => {
    mock.reset();
  });

  describe('Authentication', () => {
    it('should handle login request successfully', async () => {
      const mockResponse = { token: 'test-token' };
      mock.onPost(API_ENDPOINTS.AUTH.LOGIN).reply(200, mockResponse);

      const response = await api.login({ identifier: 'test@example.com' });
      expect(response.data).toEqual(mockResponse);
    });

    it('should handle login failure', async () => {
      mock.onPost(API_ENDPOINTS.AUTH.LOGIN).reply(401);
      
      await expect(api.login({ identifier: 'test@example.com' }))
        .rejects.toThrow('Authentication failed');
    });
  });

  describe('Expense Management', () => {
    it('should create expense successfully', async () => {
      const mockExpense = {
        description: 'Test expense',
        amount: 100
      };
      mock.onPost(API_ENDPOINTS.EXPENSES.CREATE).reply(200, mockExpense);

      const response = await api.createExpense(mockExpense);
      expect(response.data).toEqual(mockExpense);
    });

    it('should handle expense creation failure', async () => {
      mock.onPost(API_ENDPOINTS.EXPENSES.CREATE).reply(500);
      
      await expect(api.createExpense({}))
        .rejects.toThrow('Failed to create expense');
    });
  });

  describe('Error Handling', () => {
    it('should handle network errors', async () => {
      mock.onAny().networkError();
      
      await expect(api.login({}))
        .rejects.toThrow('Network error occurred');
    });

    it('should handle timeout errors', async () => {
      mock.onAny().timeout();
      
      await expect(api.login({}))
        .rejects.toThrow('Request timed out');
    });
  });
});
