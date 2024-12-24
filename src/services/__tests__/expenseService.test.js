import { fetchExpenses, addExpense, editExpense, deleteExpense, categorizeExpense } from '../expenseService';
import { expenseCategorizationAI } from '../expenseCategorizationAI';
import { offlineManager } from '../offlineManager';

// Mock dependencies
jest.mock('../expenseCategorizationAI');
jest.mock('../offlineManager');

describe('ExpenseService', () => {
  beforeEach(() => {
    // Clear all mocks
    jest.clearAllMocks();
    global.fetch = jest.fn();
    global.FormData = jest.fn(() => ({
      append: jest.fn()
    }));

    // Reset navigator.onLine
    Object.defineProperty(global.navigator, 'onLine', {
      writable: true,
      value: true
    });
  });

  describe('fetchExpenses', () => {
    it('should fetch expenses when online', async () => {
      const mockExpenses = [{ id: 1, amount: 100 }];
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ expenses: mockExpenses })
      });

      const result = await fetchExpenses();
      expect(result).toEqual(mockExpenses);
      expect(global.fetch).toHaveBeenCalledWith(expect.stringContaining('/list'));
    });

    it('should use offline manager when offline', async () => {
      Object.defineProperty(global.navigator, 'onLine', { value: false });
      const mockExpenses = [{ id: 1, amount: 100 }];
      offlineManager.getExpenses.mockResolvedValueOnce(mockExpenses);

      const result = await fetchExpenses();
      expect(result).toEqual(mockExpenses);
      expect(offlineManager.getExpenses).toHaveBeenCalled();
    });

    it('should handle fetch errors', async () => {
      global.fetch.mockRejectedValueOnce(new Error('Network error'));
      await expect(fetchExpenses()).rejects.toThrow('Network error');
    });
  });

  describe('addExpense', () => {
    const mockExpense = {
      description: 'Test expense',
      amount: 100,
      date: '2023-01-01'
    };

    it('should add expense with auto-categorization', async () => {
      const mockCategory = 'transport';
      expenseCategorizationAI.categorizeExpense.mockResolvedValueOnce({
        category: mockCategory
      });

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ id: 1, ...mockExpense, category: mockCategory })
      });

      const result = await addExpense(
        mockExpense.description,
        mockExpense.amount,
        null,
        mockExpense.date
      );

      expect(result.category).toBe(mockCategory);
      expect(expenseCategorizationAI.categorizeExpense).toHaveBeenCalled();
    });

    it('should use provided category when available', async () => {
      const providedCategory = 'food';
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ id: 1, ...mockExpense, category: providedCategory })
      });

      const result = await addExpense(
        mockExpense.description,
        mockExpense.amount,
        providedCategory,
        mockExpense.date
      );

      expect(result.category).toBe(providedCategory);
      expect(expenseCategorizationAI.categorizeExpense).not.toHaveBeenCalled();
    });

    it('should handle add expense errors', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        json: () => Promise.resolve({ error: 'Failed to add expense' })
      });

      await expect(addExpense(
        mockExpense.description,
        mockExpense.amount,
        null,
        mockExpense.date
      )).rejects.toThrow('Failed to add expense');
    });
  });

  describe('editExpense', () => {
    const mockId = 1;
    const mockUpdates = {
      amount: 150,
      description: 'Updated description'
    };

    it('should edit expense successfully', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ id: mockId, ...mockUpdates })
      });

      const result = await editExpense(mockId, mockUpdates);
      expect(result).toEqual(expect.objectContaining(mockUpdates));
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining(`/edit/${mockId}`),
        expect.any(Object)
      );
    });

    it('should handle edit expense errors', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        json: () => Promise.resolve({ error: 'Failed to edit expense' })
      });

      await expect(editExpense(mockId, mockUpdates))
        .rejects.toThrow('Failed to edit expense');
    });
  });

  describe('deleteExpense', () => {
    const mockId = 1;

    it('should delete expense successfully', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ success: true })
      });

      const result = await deleteExpense(mockId);
      expect(result).toEqual({ success: true });
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining(`/delete/${mockId}`),
        expect.any(Object)
      );
    });

    it('should handle delete expense errors', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        json: () => Promise.resolve({ error: 'Failed to delete expense' })
      });

      await expect(deleteExpense(mockId))
        .rejects.toThrow('Failed to delete expense');
    });
  });

  describe('categorizeExpense', () => {
    it('should categorize expense successfully', async () => {
      const mockDescription = 'uber ride';
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ category: 'transport' })
      });

      const result = await categorizeExpense(mockDescription);
      expect(result).toBe('transport');
    });

    it('should return Uncategorized on error', async () => {
      const mockDescription = 'invalid description';
      global.fetch.mockRejectedValueOnce(new Error('Categorization failed'));

      const result = await categorizeExpense(mockDescription);
      expect(result).toBe('Uncategorized');
      expect(console.error).toHaveBeenCalled();
    });
  });
});
