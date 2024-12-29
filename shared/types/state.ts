import { TaxCalculationResult, TaxDeduction, TaxForm } from './tax';
import { PlatformConnection, PlatformData } from './platform';

export interface TaxState {
  calculations: {
    [key: string]: TaxCalculationResult;
  };
  deductions: {
    [key: string]: TaxDeduction;
  };
  forms: {
    [key: string]: TaxForm;
  };
  loading: boolean;
  error: string | null;
}

export interface PlatformState {
  connections: {
    [key: string]: PlatformConnection;
  };
  data: {
    [key: string]: PlatformData;
  };
  syncing: boolean;
  error: string | null;
}

export interface RootState {
  tax: TaxState;
  platform: PlatformState;
  user: UserState;
}

export interface UserState {
  id: string | null;
  profile: any;
  preferences: any;
  authenticated: boolean;
}

export type Action<T = any> = {
  type: string;
  payload?: T;
  error?: boolean;
  meta?: any;
};

export type Dispatch = (action: Action) => void;
