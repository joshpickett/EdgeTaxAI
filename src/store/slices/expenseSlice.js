import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { apiClient } from '../../services/apiClient';

export const fetchExpenses = createAsyncThunk(
  'expenses/fetchAll',
  async (_, { rejectWithValue }) => {
    try {
      const response = await apiClient.getExpenses();
      return response.data;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const addExpense = createAsyncThunk(
  'expenses/add',
  async (expenseData, { rejectWithValue }) => {
    try {
      const response = await apiClient.addExpense(expenseData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const updateExpense = createAsyncThunk(
  'expenses/update',
  async ({ id, data }, { rejectWithValue }) => {
    try {
      const response = await apiClient.updateExpense(id, data);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

const initialState = {
  expenses: [],
  loading: false,
  error: null,
  selectedExpense: null
};

const expenseSlice = createSlice({
  name: 'expenses',
  initialState,
  reducers: {
    selectExpense: (state, action) => {
      state.selectedExpense = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchExpenses.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchExpenses.fulfilled, (state, action) => {
        state.loading = false;
        state.expenses = action.payload;
      })
      .addCase(fetchExpenses.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(addExpense.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(addExpense.fulfilled, (state, action) => {
        state.loading = false;
        state.expenses.push(action.payload);
      })
      .addCase(addExpense.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(updateExpense.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateExpense.fulfilled, (state, action) => {
        state.loading = false;
        const index = state.expenses.findIndex(expense => expense.id === action.payload.id);
        if (index !== -1) {
          state.expenses[index] = action.payload;
        }
      })
      .addCase(updateExpense.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  }
});

export const { selectExpense, clearError } = expenseSlice.actions;
export default expenseSlice.reducer;
