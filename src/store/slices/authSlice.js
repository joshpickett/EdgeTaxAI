// src/store/slices/authSlice.ts

import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import { UnifiedAuthService } from 'shared/services/unifiedAuthService';

const authService = UnifiedAuthService.getInstance();

export const loginUser = createAsyncThunk(
  'auth/login',
  async (credentials: any) => {
    return await authService.login(credentials);
  }
);

export const verifyOTP = createAsyncThunk(
  'auth/verifyOTP',
  async (data: any) => {
    return await authService.verifyOTP(data);
  }
);

const authSlice = createSlice({
  name: 'auth',
  initialState: {
    user: null,
    isAuthenticated: false,
    loading: false,
    error: null,
    otpSent: false,
  },
  reducers: {
    logout: (state) => {
      state.user = null;
      state.isAuthenticated = false;
      authService.logout();
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(loginUser.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.loading = false;
        state.otpSent = true;
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      });
  },
});