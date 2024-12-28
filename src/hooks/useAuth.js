import { useSelector, useDispatch } from 'react-redux';
import { loginUser, verifyOTP, logout } from 'store/slices/authSlice';
import { RootState } from 'store/types';
import { setupSrcPath } from 'setup_path';

// Initialize path setup
setupSrcPath();

export const useAuth = () => {
  const dispatch = useDispatch();
  const auth = useSelector((state: RootState) => state.auth);

  const login = async (identifier: string) => {
    try {
      await dispatch(loginUser({ identifier })).unwrap();
      return true;
    } catch (error) {
      return false;
    }
  };

  const verify = async (identifier: string, oneTimePassword: string) => {
    try {
      await dispatch(verifyOTP({ identifier, oneTimePassword })).unwrap();
      return true;
    } catch (error) {
      return false;
    }
  };

  const logoutUser = () => {
    dispatch(logout());
  };

  return {
    user: auth.user,
    isAuthenticated: auth.isAuthenticated,
    loading: auth.loading,
    error: auth.error,
    otpSent: auth.otpSent,
    login,
    verify,
    logout: logoutUser,
  };
};
