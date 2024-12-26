import configureMockStore from 'redux-mock-store';
import thunk from 'redux-thunk';
import bankIntegrationReducer, {
  generateLinkToken,
  exchangePublicToken,
  fetchBankAccounts,
  fetchTransactions,
  clearError,
  resetState
} from '../bankIntegrationSlice';
import { apiClient } from '../../../services/apiClient';

jest.mock('../../../services/apiClient');

const middlewares = [thunk];
const mockStore = configureMockStore(middlewares);

describe('bankIntegrationSlice', () => {
  let store;

  beforeEach(() => {
    store = mockStore({
      bankIntegration: {
        linkToken: null,
        accounts: [],
        transactions: [],
        loading: false,
        error: null,
        connected: false
      }
    });
    jest.clearAllMocks();
  });

  describe('reducers', () => {
    it('should handle initial state', () => {
      expect(bankIntegrationReducer(undefined, { type: 'unknown' })).toEqual({
        linkToken: null,
        accounts: [],
        transactions: [],
        loading: false,
        error: null,
        connected: false
      });
    });

    it('should handle clearError', () => {
      const state = {
        error: 'Some error',
        loading: false
      };
      expect(bankIntegrationReducer(state, clearError())).toEqual({
        error: null,
        loading: false
      });
    });

    it('should handle resetState', () => {
      const state = {
        linkToken: 'token',
        accounts: ['account1'],
        error: 'error'
      };
      expect(bankIntegrationReducer(state, resetState())).toEqual({
        linkToken: null,
        accounts: [],
        transactions: [],
        loading: false,
        error: null,
        connected: false
      });
    });
  });

  describe('async thunks', () => {
    it('should handle generateLinkToken success', async () => {
      const mockResponse = { link_token: 'test_token' };
      apiClient.post.mockResolvedValueOnce({ data: mockResponse });

      await store.dispatch(generateLinkToken());
      const actions = store.getActions();

      expect(actions[0].type).toBe(generateLinkToken.pending.type);
      expect(actions[1].type).toBe(generateLinkToken.fulfilled.type);
      expect(actions[1].payload).toEqual(mockResponse);
    });

    it('should handle generateLinkToken failure', async () => {
      const errorMessage = 'Failed to generate token';
      apiClient.post.mockRejectedValueOnce({ message: errorMessage });

      await store.dispatch(generateLinkToken());
      const actions = store.getActions();

      expect(actions[0].type).toBe(generateLinkToken.pending.type);
      expect(actions[1].type).toBe(generateLinkToken.rejected.type);
      expect(actions[1].payload).toBe(errorMessage);
    });

    it('should handle exchangePublicToken success', async () => {
      const publicToken = 'public_token';
      apiClient.post.mockResolvedValueOnce({ data: { success: true } });

      await store.dispatch(exchangePublicToken(publicToken));
      const actions = store.getActions();

      expect(actions[0].type).toBe(exchangePublicToken.pending.type);
      expect(actions[1].type).toBe(exchangePublicToken.fulfilled.type);
    });

    it('should handle fetchBankAccounts success', async () => {
      const mockAccounts = [{ id: 1, name: 'Account 1' }];
      apiClient.get.mockResolvedValueOnce({ data: mockAccounts });

      await store.dispatch(fetchBankAccounts());
      const actions = store.getActions();

      expect(actions[0].type).toBe(fetchBankAccounts.pending.type);
      expect(actions[1].type).toBe(fetchBankAccounts.fulfilled.type);
      expect(actions[1].payload).toEqual(mockAccounts);
    });

    it('should handle fetchTransactions success', async () => {
      const mockTransactions = [{ id: 1, amount: 100 }];
      const dateRange = { startDate: '2023-01-01', endDate: '2023-12-31' };
      apiClient.get.mockResolvedValueOnce({ data: mockTransactions });

      await store.dispatch(fetchTransactions(dateRange));
      const actions = store.getActions();

      expect(actions[0].type).toBe(fetchTransactions.pending.type);
      expect(actions[1].type).toBe(fetchTransactions.fulfilled.type);
      expect(actions[1].payload).toEqual(mockTransactions);
    });
  });
});
