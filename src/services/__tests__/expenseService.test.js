import { fetchExpenses, addExpense, editExpense, deleteExpense } from '../expenseService';
import { expenseCategorizationAI } from '../expenseCategorizationAI';
import { offlineManager } from '../offlineManager';

jest.mock('../expenseCategorizationAI');
jest.mock('../offlineManager');

describe('ExpenseService', () => {
  beforeEach(() => {
    global.fetch = jest.fn();
    jest.clearAllMocks();
  });

  describe('fetchExpenses', () => {
    it('fetches expenses successfully', async () => {
      const mockExpenses = [{ id: 1, amount: 100 }];
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ expenses: mockExpenses })
      });

      const result = await fetchExpenses();
      expect(result).toEqual(mockExpenses);
    });

    it('uses offline manager when offline', async () => {
      global.navigator.onLine = false;
      const mockExpenses = [{ id: 1, amount: 100 }];
      offlineManager.getExpenses.mockResolvedValueOnce(mockExpenses);

      const result = await fetchExpenses();
      expect(result).toEqual(mockExpenses);
    });
  });

  describe('addExpense', () => {
    it('adds expense with auto-categorization', async () => {
      const mockCategory = { category: 'food' };
      expenseCategorizationAI.categorizeExpense.mockResolvedValueOnce(mockCategory);
      
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ success: true })
      });

      await addExpense('Lunch', 15.99);
      expect(expenseCategorizationAI.categorizeExpense).toHaveBeenCalled();
    });
  });

  describe('editExpense', () => {
    it('edits expense successfully', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ success: true })
      });

      const result = await editExpense(1, { amount: 200 });
      expect(result).toEqual({ success: true });
    });
  });

  describe('deleteExpense', () => {
    it('deletes expense successfully', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ success: true })
      });

      const result = await deleteExpense(1);
      expect(result).toEqual({ success: true });
    });
  });
});
