import { bankService } from '../bankService';
import { apiClient } from '../apiClient';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Mock dependencies
jest.mock('../apiClient');
jest.mock('@react-native-async-storage/async-storage');

describe('BankService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('getLinkToken', () => {
    const mockUserId = 'user123';
    const mockLinkToken = 'link-token-123';

    it('should get link token successfully', async () => {
      apiClient.post.mockResolvedValueOnce({
        data: { link_token: mockLinkToken }
      });

      const result = await bankService.getLinkToken(mockUserId);

      expect(result).toBe(mockLinkToken);
      expect(apiClient.post).toHaveBeenCalledWith(
        '/api/banks/plaid/link-token',
        { user_id: mockUserId }
      );
    });

    it('should handle link token error', async () => {
      const error = new Error('Failed to get link token');
      apiClient.post.mockRejectedValueOnce(error);

      await expect(bankService.getLinkToken(mockUserId))
        .rejects.toThrow('Failed to get link token');
      expect(console.error).toHaveBeenCalled();
    });
  });

  describe('exchangeToken', () => {
    const mockPublicToken = 'public-token-123';
    const mockUserId = 'user123';
    const mockResponse = { access_token: 'access-token-123' };

    it('should exchange token successfully', async () => {
      apiClient.post.mockResolvedValueOnce({ data: mockResponse });

      const result = await bankService.exchangeToken(mockPublicToken, mockUserId);

      expect(result).toEqual(mockResponse);
      expect(apiClient.post).toHaveBeenCalledWith(
        '/api/banks/plaid/exchange-token',
        {
          public_token: mockPublicToken,
          user_id: mockUserId
        }
      );
    });

    it('should handle exchange token error', async () => {
      apiClient.post.mockRejectedValueOnce(new Error('Exchange failed'));

      await expect(bankService.exchangeToken(mockPublicToken, mockUserId))
        .rejects.toThrow('Exchange failed');
    });
  });

  describe('getTransactions', () => {
    const mockParams = { start_date: '2023-01-01', end_date: '2023-12-31' };
    const mockTransactions = [
      { id: 1, amount: 100 },
      { id: 2, amount: 200 }
    ];

    it('should fetch transactions successfully', async () => {
      apiClient.get.mockResolvedValueOnce({ data: mockTransactions });

      const result = await bankService.getTransactions(mockParams);

      expect(result).toEqual(mockTransactions);
      expect(apiClient.get).toHaveBeenCalledWith(
        '/api/banks/plaid/transactions',
        { params: mockParams }
      );
    });

    it('should handle transaction fetch error', async () => {
      apiClient.get.mockRejectedValueOnce(new Error('Failed to fetch'));

      await expect(bankService.getTransactions(mockParams))
        .rejects.toThrow('Failed to fetch');
    });
  });

  describe('getBalance', () => {
    const mockUserId = 'user123';
    const mockBalance = { available: 1000, current: 1200 };

    it('should fetch balance successfully', async () => {
      apiClient.get.mockResolvedValueOnce({ data: mockBalance });

      const result = await bankService.getBalance(mockUserId);

      expect(result).toEqual(mockBalance);
      expect(apiClient.get).toHaveBeenCalledWith(
        '/api/banks/plaid/balance',
        {
          params: { user_id: mockUserId }
        }
      );
    });

    it('should handle balance fetch error', async () => {
      apiClient.get.mockRejectedValueOnce(new Error('Failed to fetch balance'));

      await expect(bankService.getBalance(mockUserId))
        .rejects.toThrow('Failed to fetch balance');
      expect(console.error).toHaveBeenCalled();
    });
  });

  describe('disconnectBank', () => {
    const mockUserId = 'user123';
    const mockResponse = { success: true };

    it('should disconnect bank successfully', async () => {
      apiClient.post.mockResolvedValueOnce({ data: mockResponse });

      const result = await bankService.disconnectBank(mockUserId);

      expect(result).toEqual(mockResponse);
      expect(apiClient.post).toHaveBeenCalledWith(
        '/api/banks/plaid/disconnect',
        { user_id: mockUserId }
      );
    });

    it('should handle disconnect error', async () => {
      apiClient.post.mockRejectedValueOnce(new Error('Failed to disconnect'));

      await expect(bankService.disconnectBank(mockUserId))
        .rejects.toThrow('Failed to disconnect');
      expect(console.error).toHaveBeenCalled();
    });
  });

  describe('Error Handling', () => {
    it('should handle network errors', async () => {
      const networkError = new Error('Network Error');
      apiClient.get.mockRejectedValueOnce(networkError);

      await expect(bankService.getBalance('user123'))
        .rejects.toThrow('Network Error');
    });

    it('should handle API errors with custom messages', async () => {
      const apiError = {
        response: {
          data: {
            message: 'Custom API Error'
          }
        }
      };
      apiClient.get.mockRejectedValueOnce(apiError);

      await expect(bankService.getBalance('user123'))
        .rejects.toThrow('Custom API Error');
    });

    it('should handle timeout errors', async () => {
      const timeoutError = new Error('Timeout');
      apiClient.get.mockRejectedValueOnce(timeoutError);

      await expect(bankService.getBalance('user123'))
        .rejects.toThrow('Timeout');
    });
  });

  describe('Rate Limiting', () => {
    it('should handle rate limit errors', async () => {
      const rateLimitError = {
        response: {
          status: 429,
          data: {
            message: 'Too many requests'
          }
        }
      };
      apiClient.get.mockRejectedValueOnce(rateLimitError);

      await expect(bankService.getBalance('user123'))
        .rejects.toThrow('Too many requests');
    });
  });

  describe('Authentication', () => {
    it('should handle unauthorized errors', async () => {
      const unauthorizedError = {
        response: {
          status: 401,
          data: {
            message: 'Unauthorized access'
          }
        }
      };
      apiClient.get.mockRejectedValueOnce(unauthorizedError);

      await expect(bankService.getBalance('user123'))
        .rejects.toThrow('Unauthorized access');
    });
  });
});
