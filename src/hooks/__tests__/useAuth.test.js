import { renderHook, act } from '@testing-library/react-hooks';
import { useDispatch, useSelector } from 'react-redux';
import { useAuth } from 'hooks/useAuth';
import { loginUser, verifyOTP, logout } from 'store/slices/authSlice';
import { setupSrcPath } from 'setup_path';

// Initialize path setup for tests
setupSrcPath();

jest.mock('react-redux', () => ({
  useDispatch: jest.fn(),
  useSelector: jest.fn()
}));

describe('useAuth', () => {
  const mockDispatch = jest.fn();
  
  beforeEach(() => {
    useDispatch.mockReturnValue(mockDispatch);
    useSelector.mockImplementation(selector => ({
      user: null,
      isAuthenticated: false,
      loading: false,
      error: null,
      otpSent: false
    }));
  });

  it('returns auth state correctly', () => {
    const { result } = renderHook(() => useAuth());
    
    expect(result.current.user).toBeNull();
    expect(result.current.isAuthenticated).toBeFalsy();
    expect(result.current.loading).toBeFalsy();
    expect(result.current.error).toBeNull();
    expect(result.current.otpSent).toBeFalsy();
  });

  it('handles login successfully', async () => {
    mockDispatch.mockResolvedValueOnce({ payload: { success: true } });
    
    const { result } = renderHook(() => useAuth());
    
    await act(async () => {
      const success = await result.current.login('test@example.com');
      expect(success).toBeTruthy();
    });
  });

  it('handles login failure', async () => {
    mockDispatch.mockRejectedValueOnce(new Error('Login failed'));
    
    const { result } = renderHook(() => useAuth());
    
    await act(async () => {
      const success = await result.current.login('test@example.com');
      expect(success).toBeFalsy();
    });
  });

  it('handles OTP verification', async () => {
    mockDispatch.mockResolvedValueOnce({ payload: { success: true } });
    
    const { result } = renderHook(() => useAuth());
    
    await act(async () => {
      const success = await result.current.verify('test@example.com', '123456');
      expect(success).toBeTruthy();
    });
  });

  it('handles logout', () => {
    const { result } = renderHook(() => useAuth());
    
    act(() => {
      result.current.logout();
    });
    
    expect(mockDispatch).toHaveBeenCalledWith(logout());
  });
});
