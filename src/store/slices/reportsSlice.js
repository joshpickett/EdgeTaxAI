import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { apiClient } from '../../services/apiClient';

export const generateReport = createAsyncThunk(
  'reports/generate',
  async (reportParameters, { rejectWithValue }) => {
    try {
      const response = await apiClient.generateReport(reportParameters);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const fetchReportHistory = createAsyncThunk(
  'reports/fetchHistory',
  async (_, { rejectWithValue }) => {
    try {
      const response = await apiClient.getReportHistory();
      return response.data;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

const initialState = {
  currentReport: null,
  history: [],
  loading: false,
  error: null
};

const reportsSlice = createSlice({
  name: 'reports',
  initialState,
  reducers: {
    clearReportError: (state) => {
      state.error = null;
    },
    clearCurrentReport: (state) => {
      state.currentReport = null;
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(generateReport.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(generateReport.fulfilled, (state, action) => {
        state.loading = false;
        state.currentReport = action.payload;
      })
      .addCase(generateReport.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(fetchReportHistory.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchReportHistory.fulfilled, (state, action) => {
        state.loading = false;
        state.history = action.payload;
      })
      .addCase(fetchReportHistory.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  }
});

export const { clearReportError, clearCurrentReport } = reportsSlice.actions;
export default reportsSlice.reducer;
