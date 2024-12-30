export interface QueueItem {
  id: string;
  operation: string;
  params: any;
  timestamp: number;
  retryCount: number;
  status: 'pending' | 'processing' | 'completed' | 'failed';
}

export interface ProcessingResult {
  id: string;
  success: boolean;
  result?: any;
  error?: string;
}

export interface QueueStatus {
  pending: number;
  completed: number;
  failed: number;
}
