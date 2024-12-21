import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { apiClient } from '../../services/apiClient';

export const calculateTaxSavings = createAsyncThunk(
  'tax/calculateSavings',
  async (amount, { rejectWithValue }) => {
    try {
      const response = await apiClient.getTaxSavings({ amount });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const getQuarterlyEstimate = createAsyncThunk(
  'tax/quarterlyEstimate',
  async (data, { rejectWithValue }) => {
    try {
      const response = await apiClient.getQuarterlyEstimate(data);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

const initialState = {
  savings: null,
  quarterlyEstimate: null,
  loading: false,
  error: null
};

const taxSlice = createSlice({
  name: 'tax',
  initialState,
  reducers: {
    clearTaxError: (state) => {
      state.error = null;
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(calculateTaxSavings.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(calculateTaxSavings.fulfilled, (state, action) => {
        state.loading = false;
        state.savings = action.payload;
      })
      .addCase(calculateTaxSavings.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(getQuarterlyEstimate.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(getQuarterlyEstimate.fulfilled, (state, action) => {
        state.loading = false;
        state.quarterlyEstimate = action.payload;
      })
      .addCase(getQuarterlyEstimate.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  }
});

export const { clearTaxError } = taxSlice.actions;
export default taxSlice.reducer;
