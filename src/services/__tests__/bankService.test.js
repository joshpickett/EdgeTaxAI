import { bankService } from '../bankService';
import { apiClient } from '../apiClient';

jest.mock('../apiClient');

describe('BankService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('getLinkToken', () => {
    it('successfully gets link token', async () => {
      const mockResponse = { data: { link_token: 'test-token' } };
      apiClient.post.mockResolvedValueOnce(mockResponse);

      const result = await bankService.getLinkToken('user123');
      expect(result).toBe('test-token');
      expect(apiClient.post).toHaveBeenCalledWith('/api/banks/plaid/link-token', {
        user_id: 'user123'
      });
    });

    it('handles errors when getting link token', async () => {
      apiClient.post.mockRejectedValueOnce(new Error('Failed to get token'));
      await expect(bankService.getLinkToken('user123')).rejects.toThrow('Failed to get token');
    });
  });

  describe('exchangeToken', () => {
    it('successfully exchanges public token', async () => {
      const mockResponse = { data: { access_token: 'access-token' } };
      apiClient.post.mockResolvedValueOnce(mockResponse);

      const result = await bankService.exchangeToken('public-token', 'user123');
      expect(result).toEqual(mockResponse.data);
      expect(apiClient.post).toHaveBeenCalledWith('/api/banks/plaid/exchange-token', {
        public_token: 'public-token',
        user_id: 'user123'
      });
    });

    it('handles errors when exchanging token', async () => {
      apiClient.post.mockRejectedValueOnce(new Error('Exchange failed'));
      await expect(bankService.exchangeToken('public-token', 'user123')).rejects.toThrow('Exchange failed');
    });
  });

  describe('getTransactions', () => {
    it('successfully fetches transactions', async () => {
      const mockTransactions = { data: [{ id: 1, amount: 100 }] };
      apiClient.get.mockResolvedValueOnce(mockTransactions);

      const params = { startDate: '2023-01-01', endDate: '2023-12-31' };
      const result = await bankService.getTransactions(params);
      expect(result).toEqual(mockTransactions.data);
      expect(apiClient.get).toHaveBeenCalledWith('/api/banks/plaid/transactions', { params });
    });

    it('handles errors when fetching transactions', async () => {
      apiClient.get.mockRejectedValueOnce(new Error('Failed to fetch transactions'));
      await expect(bankService.getTransactions({})).rejects.toThrow('Failed to fetch transactions');
    });
  });

  describe('getBalance', () => {
    it('successfully fetches balance', async () => {
      const mockBalance = { data: { available: 1000, current: 1200 } };
      apiClient.get.mockResolvedValueOnce(mockBalance);

      const result = await bankService.getBalance('user123');
      expect(result).toEqual(mockBalance.data);
      expect(apiClient.get).toHaveBeenCalledWith('/api/banks/plaid/balance', {
        params: { user_id: 'user123' }
      });
    });

    it('handles errors when fetching balance', async () => {
      apiClient.get.mockRejectedValueOnce(new Error('Failed to fetch balance'));
      await expect(bankService.getBalance('user123')).rejects.toThrow('Failed to fetch balance');
    });
  });

  describe('disconnectBank', () => {
    it('successfully disconnects bank', async () => {
      const mockResponse = { data: { success: true } };
      apiClient.post.mockResolvedValueOnce(mockResponse);

      const result = await bankService.disconnectBank('user123');
      expect(result).toEqual(mockResponse.data);
      expect(apiClient.post).toHaveBeenCalledWith('/api/banks/plaid/disconnect', {
        user_id: 'user123'
      });
    });

    it('handles errors when disconnecting bank', async () => {
      apiClient.post.mockRejectedValueOnce(new Error('Failed to disconnect bank'));
      await expect(bankService.disconnectBank('user123')).rejects.toThrow('Failed to disconnect bank');
    });
  });
});
