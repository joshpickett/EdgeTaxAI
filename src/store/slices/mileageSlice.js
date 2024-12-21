import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { apiClient } from '../../services/apiClient';

export const calculateMileage = createAsyncThunk(
  'mileage/calculate',
  async ({ start, end }, { rejectWithValue }) => {
    try {
      const response = await apiClient.calculateMileage(start, end);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const fetchMileageHistory = createAsyncThunk(
  'mileage/fetchHistory',
  async (_, { rejectWithValue }) => {
    try {
      const response = await apiClient.getMileageHistory();
      return response.data;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

const initialState = {
  currentCalculation: null,
  history: [],
  loading: false,
  error: null
};

const mileageSlice = createSlice({
  name: 'mileage',
  initialState,
  reducers: {
    clearMileageError: (state) => {
      state.error = null;
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(calculateMileage.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(calculateMileage.fulfilled, (state, action) => {
        state.loading = false;
        state.currentCalculation = action.payload;
      })
      .addCase(calculateMileage.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(fetchMileageHistory.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchMileageHistory.fulfilled, (state, action) => {
        state.loading = false;
        state.history = action.payload;
      })
      .addCase(fetchMileageHistory.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  }
});

export const { clearMileageError } = mileageSlice.actions;
export default mileageSlice.reducer;
