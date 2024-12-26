import {
  AUTH_STATES,
  ERROR_TYPES,
  PLATFORMS,
  EXPENSE_CATEGORIES,
  TAX_CATEGORIES,
  SYNC_STATES,
  API_ENDPOINTS,
  STORAGE_KEYS,
  EVENT_TYPES
} from '../constants';

describe('Constants', () => {
  describe('AUTH_STATES', () => {
    it('should have all required auth states', () => {
      expect(AUTH_STATES.LOGGED_OUT).toBeDefined();
      expect(AUTH_STATES.LOGGING_IN).toBeDefined();
      expect(AUTH_STATES.LOGGED_IN).toBeDefined();
      expect(AUTH_STATES.ERROR).toBeDefined();
    });
  });

  describe('ERROR_TYPES', () => {
    it('should have all required error types', () => {
      expect(ERROR_TYPES.NETWORK).toBe('NETWORK_ERROR');
      expect(ERROR_TYPES.AUTH).toBe('AUTH_ERROR');
      expect(ERROR_TYPES.VALIDATION).toBe('VALIDATION_ERROR');
      expect(ERROR_TYPES.SERVER).toBe('SERVER_ERROR');
    });
  });

  describe('PLATFORMS', () => {
    it('should have all supported platforms', () => {
      expect(PLATFORMS.UBER).toBe('uber');
      expect(PLATFORMS.LYFT).toBe('lyft');
      expect(PLATFORMS.DOORDASH).toBe('doordash');
      expect(PLATFORMS.INSTACART).toBe('instacart');
    });
  });

  describe('EXPENSE_CATEGORIES', () => {
    it('should have all expense categories', () => {
      expect(EXPENSE_CATEGORIES.MILEAGE).toBe('mileage');
      expect(EXPENSE_CATEGORIES.MAINTENANCE).toBe('maintenance');
      expect(EXPENSE_CATEGORIES.INSURANCE).toBe('insurance');
      expect(EXPENSE_CATEGORIES.PHONE).toBe('phone');
      expect(EXPENSE_CATEGORIES.SUPPLIES).toBe('supplies');
      expect(EXPENSE_CATEGORIES.OTHER).toBe('other');
    });
  });

  describe('TAX_CATEGORIES', () => {
    it('should have all tax categories', () => {
      expect(TAX_CATEGORIES.DEDUCTIBLE).toBe('deductible');
      expect(TAX_CATEGORIES.NON_DEDUCTIBLE).toBe('non_deductible');
      expect(TAX_CATEGORIES.PARTIAL).toBe('partial');
    });
  });

  describe('SYNC_STATES', () => {
    it('should have all sync states', () => {
      expect(SYNC_STATES.IDLE).toBe('idle');
      expect(SYNC_STATES.SYNCING).toBe('syncing');
      expect(SYNC_STATES.COMPLETED).toBe('completed');
      expect(SYNC_STATES.ERROR).toBe('error');
    });
  });

  describe('API_ENDPOINTS', () => {
    it('should have all required API endpoints', () => {
      expect(API_ENDPOINTS.AUTH.LOGIN).toBe('/auth/login');
      expect(API_ENDPOINTS.AUTH.LOGOUT).toBe('/auth/logout');
      expect(API_ENDPOINTS.AUTH.REFRESH).toBe('/auth/refresh');
      expect(API_ENDPOINTS.EXPENSES.CREATE).toBe('/expenses');
      expect(API_ENDPOINTS.EXPENSES.LIST).toBe('/expenses/list');
    });
  });

  describe('STORAGE_KEYS', () => {
    it('should have all required storage keys', () => {
      expect(STORAGE_KEYS.AUTH_TOKEN).toBe('auth_token');
      expect(STORAGE_KEYS.REFRESH_TOKEN).toBe('refresh_token');
      expect(STORAGE_KEYS.USER_DATA).toBe('user_data');
      expect(STORAGE_KEYS.SETTINGS).toBe('settings');
    });
  });

  describe('EVENT_TYPES', () => {
    it('should have all required event types', () => {
      expect(EVENT_TYPES.AUTH_CHANGE).toBe('auth_change');
      expect(EVENT_TYPES.SYNC_STATUS).toBe('sync_status');
      expect(EVENT_TYPES.ERROR).toBe('error');
    });
  });
});
