export enum PlatformType {
  UBER = 'uber',
  LYFT = 'lyft',
  DOORDASH = 'doordash',
  INSTACART = 'instacart',
  OTHER = 'other'
}

export interface PlatformCredentials {
  platformId: string;
  accessToken: string;
  refreshToken: string;
  expiresAt: string;
}

export interface PlatformConnection {
  id: string;
  userId: string;
  platform: PlatformType;
  credentials: PlatformCredentials;
  lastSync: string;
  status: ConnectionStatus;
}

export enum ConnectionStatus {
  ACTIVE = 'active',
  EXPIRED = 'expired',
  REVOKED = 'revoked',
  ERROR = 'error'
}

export interface PlatformData {
  platform: PlatformType;
  earnings: number;
  expenses: number;
  mileage: number;
  trips: number;
  startDate: string;
  endDate: string;
  raw?: any;
}

export interface SyncResult {
  success: boolean;
  platformId: string;
  syncedData: PlatformData;
  errors?: Array<{
    code: string;
    message: string;
  }>;
  timestamp: string;
}
