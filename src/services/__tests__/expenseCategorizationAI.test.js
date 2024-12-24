import { expenseCategorizationAI } from '../expenseCategorizationAI';
import { apiClient } from '../apiClient';

// Mock dependencies
jest.mock('../apiClient');

describe('ExpenseCategorizationAI', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Reset navigator.onLine
    Object.defineProperty(global.navigator, 'onLine', {
      writable: true,
      value: true
    });
  });

  describe('categorizeExpense', () => {
    const mockExpense = {
      description: 'uber ride to airport',
      amount: 50,
      date: '2023-01-01'
    };

    it('should use online categorization when connected', async () => {
      const mockResponse = { 
        category: 'transport',
        confidence: 0.95,
        method: 'online'
      };
      apiClient.post.mockResolvedValueOnce({ data: mockResponse });

      const result = await expenseCategorizationAI.categorizeExpense(mockExpense);
      expect(result).toEqual(mockResponse);
      expect(apiClient.post).toHaveBeenCalledWith(
        '/expenses/categorize',
        mockExpense
      );
    });

    it('should fallback to offline categorization when offline', async () => {
      Object.defineProperty(global.navigator, 'onLine', { value: false });
      
      const result = await expenseCategorizationAI.categorizeExpense(mockExpense);
      expect(result.category).toBe('transport');
      expect(result.method).toBe('offline');
      expect(apiClient.post).not.toHaveBeenCalled();
    });

    it('should fallback to offline categorization on API error', async () => {
      apiClient.post.mockRejectedValueOnce(new Error('API Error'));
      
      const result = await expenseCategorizationAI.categorizeExpense(mockExpense);
      expect(result.method).toBe('offline');
      expect(console.error).toHaveBeenCalled();
    });
  });

  describe('offlineCategorizationRequest', () => {
    it('should categorize large expenses correctly', () => {
      const expense = {
        description: 'new laptop',
        amount: 1500
      };

      const result = expenseCategorizationAI.offlineCategorizationRequest(expense);
      expect(result).toEqual({
        category: 'large-expense',
        confidence: 0.9,
        method: 'offline'
      });
    });

    it('should match keywords for categories', () => {
      const expense = {
        description: 'lunch at restaurant',
        amount: 25
      };

      const result = expenseCategorizationAI.offlineCategorizationRequest(expense);
      expect(result.category).toBe('meals');
      expect(result.confidence).toBe(0.8);
    });

    it('should return other category when no match found', () => {
      const expense = {
        description: 'miscellaneous item',
        amount: 30
      };

      const result = expenseCategorizationAI.offlineCategorizationRequest(expense);
      expect(result.category).toBe('other');
      expect(result.confidence).toBe(0.5);
    });
  });

  describe('trainModel', () => {
    const mockTrainingData = [
      { description: 'uber', category: 'transport' },
      { description: 'coffee', category: 'meals' }
    ];

    it('should successfully train the model', async () => {
      apiClient.post.mockResolvedValueOnce({ 
        data: { success: true, message: 'Model trained successfully' }
      });

      const result = await expenseCategorizationAI.trainModel(mockTrainingData);
      expect(result.success).toBe(true);
      expect(apiClient.post).toHaveBeenCalledWith('/ai/train', mockTrainingData);
    });

    it('should handle training errors', async () => {
      apiClient.post.mockRejectedValueOnce(new Error('Training failed'));
      
      await expect(expenseCategorizationAI.trainModel(mockTrainingData))
        .rejects.toThrow('Training failed');
      expect(console.error).toHaveBeenCalled();
    });
  });

  describe('getCategorizationSuggestions', () => {
    const mockExpense = {
      description: 'office supplies',
      amount: 75
    };

    it('should return suggestions successfully', async () => {
      const mockSuggestions = [
        { category: 'supplies', confidence: 0.9 },
        { category: 'equipment', confidence: 0.7 }
      ];
      apiClient.post.mockResolvedValueOnce({ 
        data: { suggestions: mockSuggestions }
      });

      const result = await expenseCategorizationAI.getCategorizationSuggestions(mockExpense);
      expect(result).toEqual(mockSuggestions);
      expect(apiClient.post).toHaveBeenCalledWith('/ai/suggestions', mockExpense);
    });

    it('should handle API errors and return empty array', async () => {
      apiClient.post.mockRejectedValueOnce(new Error('API Error'));
      
      const result = await expenseCategorizationAI.getCategorizationSuggestions(mockExpense);
      expect(result).toEqual([]);
      expect(console.error).toHaveBeenCalled();
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty description', async () => {
      const expense = {
        description: '',
        amount: 50
      };

      const result = await expenseCategorizationAI.categorizeExpense(expense);
      expect(result.category).toBe('other');
    });

    it('should handle special characters in description', async () => {
      const expense = {
        description: '!@#$%^&* special chars',
        amount: 50
      };

      const result = await expenseCategorizationAI.categorizeExpense(expense);
      expect(result).toBeDefined();
    });

    it('should handle negative amounts', async () => {
      const expense = {
        description: 'refund',
        amount: -50
      };

      const result = await expenseCategorizationAI.categorizeExpense(expense);
      expect(result).toBeDefined();
    });
  });
});
