import { DocumentType, StorageOptions, StorageResult } from '../types/documents';
import { ApiClient } from './apiClient';
import { OfflineQueueManager } from './offlineQueueManager';
import { errorHandler } from './errorHandler';

export class DocumentStorageService {
  private apiClient: ApiClient;
  private offlineQueue: OfflineQueueManager;
  private readonly ALLOWED_TYPES = ['image/jpeg', 'image/png', 'application/pdf'];
  private readonly MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

  constructor() {
    this.apiClient = new ApiClient();
    this.offlineQueue = new OfflineQueueManager();
  }

  async storeDocument(file: File, options: StorageOptions = {}): Promise<StorageResult> {
    try {
      this.validateFile(file);

      if (!navigator.onLine) {
        return this.handleOfflineStorage(file, options);
      }

      const formData = new FormData();
      formData.append('document', file);
      formData.append('metadata', JSON.stringify(options));

      const response = await this.apiClient.post('/documents/store', formData);
      return this.processStorageResponse(response);
    } catch (error) {
      return errorHandler.handleError(error, {
        component: 'DocumentStorageService',
        operation: 'storeDocument',
        retryCount: 0,
        maxRetries: 3
      });
    }
  }

  async retrieveDocument(documentId: string): Promise<Blob> {
    try {
      const response = await this.apiClient.get(`/documents/${documentId}`, {
        responseType: 'blob'
      });
      return response.data;
    } catch (error) {
      throw errorHandler.handleError(error, {
        component: 'DocumentStorageService',
        operation: 'retrieveDocument',
        retryCount: 0,
        maxRetries: 3
      });
    }
  }

  private validateFile(file: File): void {
    if (!this.ALLOWED_TYPES.includes(file.type)) {
      throw new Error('Invalid file type');
    }
    if (file.size > this.MAX_FILE_SIZE) {
      throw new Error('File size exceeds maximum allowed size');
    }
  }

  private async handleOfflineStorage(file: File, options: StorageOptions): Promise<StorageResult> {
    await this.offlineQueue.addToQueue('storeDocument', { file, options });
    return {
      status: 'queued',
      documentId: `offline_${Date.now()}`,
      message: 'Document will be stored when online'
    };
  }

  private processStorageResponse(response: any): StorageResult {
    return {
      status: 'stored',
      documentId: response.data.documentId,
      url: response.data.url,
      metadata: response.data.metadata
    };
  }
}

export const documentStorageService = new DocumentStorageService();
