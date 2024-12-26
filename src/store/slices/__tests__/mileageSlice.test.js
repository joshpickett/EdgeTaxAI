import configureMockStore from 'redux-mock-store';
import thunk from 'redux-thunk';
import mileageReducer, {
  calculateMileage,
  fetchMileageHistory,
  clearMileageError
} from '../mileageSlice';
import { apiClient } from '../../../services/apiClient';

jest.mock('../../../services/apiClient');

const middlewares = [thunk];
const mockStore = configureMockStore(middlewares);

describe('mileageSlice', () => {
  let store;

  beforeEach(() => {
    store = mockStore({
      mileage: {
        currentCalculation: null,
        history: [],
        loading: false,
        error: null
      }
    });
    jest.clearAllMocks();
  });

  describe('reducers', () => {
    it('should handle initial state', () => {
      expect(mileageReducer(undefined, { type: 'unknown' })).toEqual({
        currentCalculation: null,
        history: [],
        loading: false,
        error: null
      });
    });

    it('should handle clearMileageError', () => {
      const state = {
        error: 'Some error',
        loading: false
      };
      expect(mileageReducer(state, clearMileageError())).toEqual({
        error: null,
        loading: false
      });
    });
  });

  describe('async thunks', () => {
    it('should handle calculateMileage success', async () => {
      const mockData = { distance: 100, cost: 50 };
      const params = { start: 'A', end: 'B' };
      apiClient.calculateMileage.mockResolvedValueOnce({ data: mockData });

      await store.dispatch(calculateMileage(params));
      const actions = store.getActions();

      expect(actions[0].type).toBe(calculateMileage.pending.type);
      expect(actions[1].type).toBe(calculateMileage.fulfilled.type);
      expect(actions[1].payload).toEqual(mockData);
    });

    it('should handle calculateMileage failure', async () => {
      const errorMessage = 'Failed to calculate mileage';
      const params = { start: 'A', end: 'B' };
      apiClient.calculateMileage.mockRejectedValueOnce({ message: errorMessage });

      await store.dispatch(calculateMileage(params));
      const actions = store.getActions();

      expect(actions[0].type).toBe(calculateMileage.pending.type);
      expect(actions[1].type).toBe(calculateMileage.rejected.type);
      expect(actions[1].payload).toBe(errorMessage);
    });

    it('should handle fetchMileageHistory success', async () => {
      const mockHistory = [{ id: 1, distance: 100 }];
      apiClient.getMileageHistory.mockResolvedValueOnce({ data: mockHistory });

      await store.dispatch(fetchMileageHistory());
      const actions = store.getActions();

      expect(actions[0].type).toBe(fetchMileageHistory.pending.type);
      expect(actions[1].type).toBe(fetchMileageHistory.fulfilled.type);
      expect(actions[1].payload).toEqual(mockHistory);
    });
  });
});
