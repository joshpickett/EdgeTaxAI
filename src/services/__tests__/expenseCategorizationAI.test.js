import { expenseCategorizationAI } from '../expenseCategorizationAI';
import { apiClient } from '../apiClient';

jest.mock('../apiClient');

describe('ExpenseCategorizationAI', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('categorizeExpense', () => {
    const mockExpense = {
      description: 'Uber ride',
      amount: 25.50,
      date: '2023-01-01'
    };

    it('uses online categorization when online', async () => {
      global.navigator.onLine = true;
      const mockResponse = { data: { category: 'transport', confidence: 0.95 } };
      apiClient.post.mockResolvedValueOnce(mockResponse);

      const result = await expenseCategorizationAI.categorizeExpense(mockExpense);
      expect(result).toEqual(mockResponse.data);
      expect(apiClient.post).toHaveBeenCalledWith('/expenses/categorize', mockExpense);
    });

    it('uses offline categorization when offline', async () => {
      global.navigator.onLine = false;
      
      const result = await expenseCategorizationAI.categorizeExpense(mockExpense);
      expect(result.category).toBe('transport');
      expect(result.method).toBe('offline');
    });

    it('handles API errors gracefully', async () => {
      global.navigator.onLine = true;
      apiClient.post.mockRejectedValueOnce(new Error('API Error'));

      const result = await expenseCategorizationAI.categorizeExpense(mockExpense);
      expect(result.method).toBe('offline');
    });
  });

  describe('trainModel', () => {
    it('sends training data successfully', async () => {
      const mockTrainingData = [
        { description: 'test', category: 'food' }
      ];
      const mockResponse = { data: { success: true } };
      apiClient.post.mockResolvedValueOnce(mockResponse);

      await expenseCategorizationAI.trainModel(mockTrainingData);
      expect(apiClient.post).toHaveBeenCalledWith('/ai/train', mockTrainingData);
    });
  });
});
