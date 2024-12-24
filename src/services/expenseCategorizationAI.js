import { apiClient } from './apiClient';

class ExpenseCategorizationAI {
  constructor() {
    this.categories = {
      transport: ['uber', 'lyft', 'taxi', 'gas', 'parking'],
      meals: ['restaurant', 'food', 'cafe', 'coffee', 'lunch', 'dinner', 'breakfast'],
      supplies: ['office', 'supplies', 'equipment'],
      utilities: ['phone', 'internet', 'electricity'],
      marketing: ['advertising', 'promotion', 'marketing'],
      entertainment: ['movies', 'theatre', 'concert', 'show'],
      travel: ['hotel', 'airfare', 'flight', 'lodging'],
      insurance: ['insurance', 'coverage', 'policy']
    };
  }

  async categorizeExpense(expense) {
    try {
      // Try online categorization first
      if (navigator.onLine) {
        return await this.onlineCategorizationRequest(expense);
      }
      
      // Fallback to offline categorization
      return this.offlineCategorizationRequest(expense);
    } catch (error) {
      console.error('Categorization error:', error);
      return this.offlineCategorizationRequest(expense);
    }
  }

  async onlineCategorizationRequest(expense) {
    try {
      const response = await apiClient.post('/expenses/categorize', {
        description: expense.description,
        amount: expense.amount,
        date: expense.date,
      });
      
      return response.data;
    } catch (error) {
      console.error('Online categorization error:', error);
      throw error;
    }
  }

  offlineCategorizationRequest(expense) {
    const description = expense.description.toLowerCase();
    
    // Check for amount-based categorization
    if (expense.amount > 1000) {
      return { category: 'large-expense', confidence: 0.9, method: 'offline' };
    }

    // Check each category's keywords
    for (const [category, keywords] of Object.entries(this.categories)) {
      if (keywords.some(keyword => description.includes(keyword))) {
        return {
          category,
          confidence: 0.8,
          method: 'offline',
        };
      }
    }

    // Default categorization
    return {
      category: 'other',
      confidence: 0.5,
      method: 'offline',
    };
  }

  async trainModel(trainingData) {
    try {
      const response = await apiClient.post('/ai/train', trainingData);
      return response.data;
    } catch (error) {
      console.error('Error training model:', error);
      throw error;
    }
  }

  async getCategorizationSuggestions(expense) {
    try {
      const response = await apiClient.post('/ai/suggestions', expense);
      return response.data.suggestions;
    } catch (error) {
      console.error('Error getting suggestions:', error);
      return [];
    }
  }
}

export const expenseCategorizationAI = new ExpenseCategorizationAI();
