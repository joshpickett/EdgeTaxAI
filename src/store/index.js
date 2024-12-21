import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import expenseReducer from './slices/expenseSlice';
import taxReducer from './slices/taxSlice';
import bankIntegrationReducer from './slices/bankIntegrationSlice';
import gigPlatformReducer from './slices/gigPlatformSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    expenses: expenseReducer,
    tax: taxReducer,
    bankIntegration: bankIntegrationReducer,
    gigPlatform: gigPlatformReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false,
    }),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
