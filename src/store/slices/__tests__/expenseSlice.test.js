import configureMockStore from 'redux-mock-store';
import thunk from 'redux-thunk';
import expenseReducer, {
  fetchExpenses,
  addExpense,
  updateExpense,
  selectExpense,
  clearError
} from '../expenseSlice';
import { apiClient } from '../../../services/apiClient';

jest.mock('../../../services/apiClient');

const middlewares = [thunk];
const mockStore = configureMockStore(middlewares);

describe('expenseSlice', () => {
  let store;

  beforeEach(() => {
    store = mockStore({
      expenses: {
        expenses: [],
        loading: false,
        error: null,
        selectedExpense: null
      }
    });
    jest.clearAllMocks();
  });

  describe('reducers', () => {
    it('should handle initial state', () => {
      expect(expenseReducer(undefined, { type: 'unknown' })).toEqual({
        expenses: [],
        loading: false,
        error: null,
        selectedExpense: null
      });
    });

    it('should handle selectExpense', () => {
      const expense = { id: 1, amount: 100 };
      expect(expenseReducer(undefined, selectExpense(expense))).toEqual({
        expenses: [],
        loading: false,
        error: null,
        selectedExpense: expense
      });
    });

    it('should handle clearError', () => {
      const initialState = {
        expenses: [],
        loading: false,
        error: 'Some error',
        selectedExpense: null
      };
      expect(expenseReducer(initialState, clearError())).toEqual({
        ...initialState,
        error: null
      });
    });
  });

  describe('async thunks', () => {
    it('should handle fetchExpenses success', async () => {
      const mockExpenses = [{ id: 1, amount: 100 }];
      apiClient.getExpenses.mockResolvedValueOnce({ data: mockExpenses });

      await store.dispatch(fetchExpenses());
      const actions = store.getActions();

      expect(actions[0].type).toBe(fetchExpenses.pending.type);
      expect(actions[1].type).toBe(fetchExpenses.fulfilled.type);
      expect(actions[1].payload).toEqual(mockExpenses);
    });

    it('should handle addExpense success', async () => {
      const newExpense = { amount: 100, description: 'Test' };
      const mockResponse = { id: 1, ...newExpense };
      apiClient.addExpense.mockResolvedValueOnce({ data: mockResponse });

      await store.dispatch(addExpense(newExpense));
      const actions = store.getActions();

      expect(actions[0].type).toBe(addExpense.pending.type);
      expect(actions[1].type).toBe(addExpense.fulfilled.type);
      expect(actions[1].payload).toEqual(mockResponse);
    });

    it('should handle updateExpense success', async () => {
      const updatedExpense = { id: 1, amount: 200 };
      apiClient.updateExpense.mockResolvedValueOnce({ data: updatedExpense });

      await store.dispatch(updateExpense({ id: 1, data: { amount: 200 } }));
      const actions = store.getActions();

      expect(actions[0].type).toBe(updateExpense.pending.type);
      expect(actions[1].type).toBe(updateExpense.fulfilled.type);
      expect(actions[1].payload).toEqual(updatedExpense);
    });

    it('should handle fetch error', async () => {
      const errorMessage = 'Failed to fetch';
      apiClient.getExpenses.mockRejectedValueOnce({ message: errorMessage });

      await store.dispatch(fetchExpenses());
      const actions = store.getActions();

      expect(actions[0].type).toBe(fetchExpenses.pending.type);
      expect(actions[1].type).toBe(fetchExpenses.rejected.type);
      expect(actions[1].payload).toBe(errorMessage);
    });
  });
});
