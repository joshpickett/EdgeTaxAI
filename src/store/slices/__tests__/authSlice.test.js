import authReducer, { 
  loginUser, 
  verifyOneTimePassword, 
  logout, 
  clearError 
} from '../authSlice';
import { apiClient } from '../../../services/apiClient';

jest.mock('../../../services/apiClient');

describe('authSlice', () => {
  const initialState = {
    user: null,
    token: null,
    isAuthenticated: false,
    loading: false,
    error: null,
    otpSent: false
  };

  describe('reducers', () => {
    it('should handle initial state', () => {
      expect(authReducer(undefined, { type: 'unknown' })).toEqual(initialState);
    });

    it('should handle logout', () => {
      const state = {
        ...initialState,
        user: { id: 1 },
        token: 'token',
        isAuthenticated: true
      };
      
      expect(authReducer(state, logout())).toEqual(initialState);
    });

    it('should handle clearError', () => {
      const state = {
        ...initialState,
        error: 'Some error'
      };
      
      expect(authReducer(state, clearError())).toEqual({
        ...state,
        error: null
      });
    });
  });

  describe('async thunks', () => {
    it('handles successful login', async () => {
      const credentials = { email: 'test@example.com', password: 'password' };
      const mockResponse = { data: { success: true } };
      
      apiClient.login.mockResolvedValueOnce(mockResponse);
      
      const dispatch = jest.fn();
      const thunk = loginUser(credentials);
      await thunk(dispatch, () => ({}));
      
      const { calls } = dispatch.mock;
      expect(calls[0][0].type).toBe('auth/login/pending');
      expect(calls[1][0].type).toBe('auth/login/fulfilled');
    });

    it('handles failed login', async () => {
      const credentials = { email: 'test@example.com', password: 'wrong' };
      apiClient.login.mockRejectedValueOnce(new Error('Invalid credentials'));
      
      const dispatch = jest.fn();
      const thunk = loginUser(credentials);
      await thunk(dispatch, () => ({}));
      
      const { calls } = dispatch.mock;
      expect(calls[1][0].type).toBe('auth/login/rejected');
    });
  });
});
