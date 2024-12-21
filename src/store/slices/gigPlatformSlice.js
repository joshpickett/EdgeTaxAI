import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { apiClient } from '../../services/apiClient';

export const connectPlatform = createAsyncThunk(
  'gig/connect',
  async ({ platform, authCode }, { rejectWithValue }) => {
    try {
      const response = await apiClient.post(`/gig/connect/${platform}`, { auth_code: authCode });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const fetchConnectedPlatforms = createAsyncThunk(
  'gig/fetchConnected',
  async (_, { rejectWithValue }) => {
    try {
      const response = await apiClient.get('/gig/connections');
      return response.data;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const fetchPlatformData = createAsyncThunk(
  'gig/fetchData',
  async ({ platform, startDate, endDate }, { rejectWithValue }) => {
    try {
      const response = await apiClient.get(`/gig/fetch-data/${platform}`, {
        params: { start_date: startDate, end_date: endDate }
      });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const disconnectPlatform = createAsyncThunk(
  'gig/disconnect',
  async (platform, { rejectWithValue }) => {
    try {
      const response = await apiClient.post(`/gig/disconnect/${platform}`);
      return { platform, ...response.data };
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

const initialState = {
  connectedPlatforms: [],
  platformData: {},
  loading: false,
  error: null,
  currentPlatform: null
};

const gigPlatformSlice = createSlice({
  name: 'gigPlatform',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    setCurrentPlatform: (state, action) => {
      state.currentPlatform = action.payload;
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(connectPlatform.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(connectPlatform.fulfilled, (state, action) => {
        state.loading = false;
        if (!state.connectedPlatforms.includes(action.payload.platform)) {
          state.connectedPlatforms.push(action.payload.platform);
        }
      })
      .addCase(connectPlatform.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(fetchConnectedPlatforms.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchConnectedPlatforms.fulfilled, (state, action) => {
        state.loading = false;
        state.connectedPlatforms = action.payload;
      })
      .addCase(fetchConnectedPlatforms.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(fetchPlatformData.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchPlatformData.fulfilled, (state, action) => {
        state.loading = false;
        state.platformData[action.payload.platform] = action.payload.data;
      })
      .addCase(fetchPlatformData.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(disconnectPlatform.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(disconnectPlatform.fulfilled, (state, action) => {
        state.loading = false;
        state.connectedPlatforms = state.connectedPlatforms.filter(
          platform => platform !== action.payload.platform
        );
        delete state.platformData[action.payload.platform];
      })
      .addCase(disconnectPlatform.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  }
});

export const { clearError, setCurrentPlatform } = gigPlatformSlice.actions;
export default gigPlatformSlice.reducer;
