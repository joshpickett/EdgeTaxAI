import { apiClient } from './apiClient';
import AsyncStorage from '@react-native-async-storage/async-storage';

class BankService {
  constructor() {
    this.baseUrl = '/api/banks/plaid';
  }

  async getLinkToken(userId) {
    try {
      const response = await apiClient.post(`${this.baseUrl}/link-token`, { user_id: userId });
      return response.data.link_token;
    } catch (error) {
      console.error('Error getting link token:', error);
      throw error;
    }
  }

  async exchangeToken(publicToken, userId) {
    try {
      const response = await apiClient.post(`${this.baseUrl}/exchange-token`, {
        public_token: publicToken,
        user_id: userId
      });
      return response.data;
    } catch (error) {
      console.error('Error exchanging token:', error);
      throw error;
    }
  }

  async getTransactions(params) {
    try {
      const response = await apiClient.get(`${this.baseUrl}/transactions`, { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching transactions:', error);
      throw error;
    }
  }

  async getBalance(userId) {
    try {
      const response = await apiClient.get(`${this.baseUrl}/balance`, {
        params: { user_id: userId }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching balance:', error);
      throw error;
    }
  }

  async disconnectBank(userId) {
    try {
      const response = await apiClient.post(`${this.baseUrl}/disconnect`, { user_id: userId });
      return response.data;
    } catch (error) {
      console.error('Error disconnecting bank:', error);
      throw error;
    }
  }
}

export const bankService = new BankService();
