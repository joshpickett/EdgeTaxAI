import configureMockStore from 'redux-mock-store';
import thunk from 'redux-thunk';
import gigPlatformReducer, {
  connectPlatform,
  fetchConnectedPlatforms,
  fetchPlatformData,
  disconnectPlatform,
  clearError,
  setCurrentPlatform
} from '../gigPlatformSlice';
import { apiClient } from '../../../services/apiClient';

jest.mock('../../../services/apiClient');

const middlewares = [thunk];
const mockStore = configureMockStore(middlewares);

describe('gigPlatformSlice', () => {
  let store;

  beforeEach(() => {
    store = mockStore({
      gigPlatform: {
        connectedPlatforms: [],
        platformData: {},
        loading: false,
        error: null,
        currentPlatform: null
      }
    });
    jest.clearAllMocks();
  });

  describe('reducers', () => {
    it('should handle initial state', () => {
      expect(gigPlatformReducer(undefined, { type: 'unknown' })).toEqual({
        connectedPlatforms: [],
        platformData: {},
        loading: false,
        error: null,
        currentPlatform: null
      });
    });

    it('should handle setCurrentPlatform', () => {
      const platform = 'uber';
      expect(gigPlatformReducer(undefined, setCurrentPlatform(platform))).toEqual({
        connectedPlatforms: [],
        platformData: {},
        loading: false,
        error: null,
        currentPlatform: platform
      });
    });

    it('should handle clearError', () => {
      const initialState = {
        connectedPlatforms: [],
        platformData: {},
        loading: false,
        error: 'Some error',
        currentPlatform: null
      };
      expect(gigPlatformReducer(initialState, clearError())).toEqual({
        ...initialState,
        error: null
      });
    });
  });

  describe('async thunks', () => {
    it('should handle connectPlatform success', async () => {
      const platform = 'uber';
      const authCode = '123456';
      const mockResponse = { platform, status: 'connected' };
      
      apiClient.post.mockResolvedValueOnce({ data: mockResponse });

      await store.dispatch(connectPlatform({ platform, authCode }));
      const actions = store.getActions();

      expect(actions[0].type).toBe(connectPlatform.pending.type);
      expect(actions[1].type).toBe(connectPlatform.fulfilled.type);
      expect(actions[1].payload).toEqual(mockResponse);
    });

    it('should handle fetchConnectedPlatforms success', async () => {
      const mockPlatforms = ['uber', 'lyft'];
      apiClient.get.mockResolvedValueOnce({ data: mockPlatforms });

      await store.dispatch(fetchConnectedPlatforms());
      const actions = store.getActions();

      expect(actions[0].type).toBe(fetchConnectedPlatforms.pending.type);
      expect(actions[1].type).toBe(fetchConnectedPlatforms.fulfilled.type);
      expect(actions[1].payload).toEqual(mockPlatforms);
    });

    it('should handle disconnectPlatform success', async () => {
      const platform = 'uber';
      const mockResponse = { success: true };
      apiClient.post.mockResolvedValueOnce({ data: mockResponse });

      await store.dispatch(disconnectPlatform(platform));
      const actions = store.getActions();

      expect(actions[0].type).toBe(disconnectPlatform.pending.type);
      expect(actions[1].type).toBe(disconnectPlatform.fulfilled.type);
      expect(actions[1].payload).toEqual({ platform, ...mockResponse });
    });

    it('should handle fetch error', async () => {
      const errorMessage = 'Failed to fetch platforms';
      apiClient.get.mockRejectedValueOnce({ message: errorMessage });

      await store.dispatch(fetchConnectedPlatforms());
      const actions = store.getActions();

      expect(actions[0].type).toBe(fetchConnectedPlatforms.pending.type);
      expect(actions[1].type).toBe(fetchConnectedPlatforms.rejected.type);
      expect(actions[1].payload).toBe(errorMessage);
    });
  });
});
