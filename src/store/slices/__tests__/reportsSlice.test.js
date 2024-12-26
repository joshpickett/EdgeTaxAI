import configureMockStore from 'redux-mock-store';
import thunk from 'redux-thunk';
import reportsReducer, {
  generateReport,
  fetchReportHistory,
  clearReportError,
  clearCurrentReport
} from '../reportsSlice';
import { apiClient } from '../../../services/apiClient';

jest.mock('../../../services/apiClient');

const middlewares = [thunk];
const mockStore = configureMockStore(middlewares);

describe('reportsSlice', () => {
  let store;

  beforeEach(() => {
    store = mockStore({
      reports: {
        currentReport: null,
        history: [],
        loading: false,
        error: null
      }
    });
    jest.clearAllMocks();
  });

  describe('reducers', () => {
    it('should handle initial state', () => {
      expect(reportsReducer(undefined, { type: 'unknown' })).toEqual({
        currentReport: null,
        history: [],
        loading: false,
        error: null
      });
    });

    it('should handle clearReportError', () => {
      const state = {
        error: 'Some error',
        loading: false
      };
      expect(reportsReducer(state, clearReportError())).toEqual({
        error: null,
        loading: false
      });
    });

    it('should handle clearCurrentReport', () => {
      const state = {
        currentReport: { id: 1 },
        loading: false
      };
      expect(reportsReducer(state, clearCurrentReport())).toEqual({
        currentReport: null,
        loading: false
      });
    });
  });

  describe('async thunks', () => {
    it('should handle generateReport success', async () => {
      const mockReport = { id: 1, data: 'report data' };
      const params = { startDate: '2023-01-01', endDate: '2023-12-31' };
      apiClient.generateReport.mockResolvedValueOnce({ data: mockReport });

      await store.dispatch(generateReport(params));
      const actions = store.getActions();

      expect(actions[0].type).toBe(generateReport.pending.type);
      expect(actions[1].type).toBe(generateReport.fulfilled.type);
      expect(actions[1].payload).toEqual(mockReport);
    });

    it('should handle fetchReportHistory success', async () => {
      const mockHistory = [{ id: 1, date: '2023-01-01' }];
      apiClient.getReportHistory.mockResolvedValueOnce({ data: mockHistory });

      await store.dispatch(fetchReportHistory());
      const actions = store.getActions();

      expect(actions[0].type).toBe(fetchReportHistory.pending.type);
      expect(actions[1].type).toBe(fetchReportHistory.fulfilled.type);
      expect(actions[1].payload).toEqual(mockHistory);
    });

    it('should handle generateReport failure', async () => {
      const errorMessage = 'Failed to generate report';
      const params = { startDate: '2023-01-01', endDate: '2023-12-31' };
      apiClient.generateReport.mockRejectedValueOnce({ message: errorMessage });

      await store.dispatch(generateReport(params));
      const actions = store.getActions();

      expect(actions[0].type).toBe(generateReport.pending.type);
      expect(actions[1].type).toBe(generateReport.rejected.type);
      expect(actions[1].payload).toBe(errorMessage);
    });
  });
});
