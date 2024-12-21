import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { apiClient } from '../../services/apiClient';

export const generateLinkToken = createAsyncThunk(
  'bank/generateLinkToken',
  async (_, { rejectWithValue }) => {
    try {
      const response = await apiClient.post('/banks/link-token');
      return response.data;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const exchangePublicToken = createAsyncThunk(
  'bank/exchangeToken',
  async (publicToken, { rejectWithValue }) => {
    try {
      const response = await apiClient.post('/banks/exchange-token', { public_token: publicToken });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const fetchBankAccounts = createAsyncThunk(
  'bank/fetchAccounts',
  async (_, { rejectWithValue }) => {
    try {
      const response = await apiClient.get('/banks/accounts');
      return response.data;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const fetchTransactions = createAsyncThunk(
  'bank/fetchTransactions',
  async ({ startDate, endDate }, { rejectWithValue }) => {
    try {
      const response = await apiClient.get('/banks/transactions', {
        params: { start_date: startDate, end_date: endDate }
      });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

const initialState = {
  linkToken: null,
  accounts: [],
  transactions: [],
  loading: false,
  error: null,
  connected: false
};

const bankIntegrationSlice = createSlice({
  name: 'bankIntegration',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    resetState: () => initialState
  },
  extraReducers: (builder) => {
    builder
      .addCase(generateLinkToken.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(generateLinkToken.fulfilled, (state, action) => {
        state.loading = false;
        state.linkToken = action.payload.link_token;
      })
      .addCase(generateLinkToken.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(exchangePublicToken.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(exchangePublicToken.fulfilled, (state) => {
        state.loading = false;
        state.connected = true;
      })
      .addCase(exchangePublicToken.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(fetchBankAccounts.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchBankAccounts.fulfilled, (state, action) => {
        state.loading = false;
        state.accounts = action.payload;
      })
      .addCase(fetchBankAccounts.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(fetchTransactions.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchTransactions.fulfilled, (state, action) => {
        state.loading = false;
        state.transactions = action.payload;
      })
      .addCase(fetchTransactions.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  }
});

export const { clearError, resetState } = bankIntegrationSlice.actions;
export default bankIntegrationSlice.reducer;
