import { DocumentHistory, HistoryEntry, DocumentVersion } from '../types/documents';
import { ApiClient } from './apiClient';
import { errorHandler } from './errorHandler';

export class DocumentHistoryService {
  private apiClient: ApiClient;

  constructor() {
    this.apiClient = new ApiClient();
  }

  async getDocumentHistory(documentId: string): Promise<DocumentHistory> {
    try {
      const response = await this.apiClient.get(`/documents/${documentId}/history`);
      return this.processHistoryResponse(response.data);
    } catch (error) {
      throw errorHandler.handleError(error, {
        component: 'DocumentHistoryService',
        operation: 'getDocumentHistory',
        retryCount: 0,
        maxRetries: 3
      });
    }
  }

  async createVersion(documentId: string, changes: any): Promise<DocumentVersion> {
    try {
      const response = await this.apiClient.post(`/documents/${documentId}/versions`, {
        changes
      });
      return response.data;
    } catch (error) {
      throw errorHandler.handleError(error, {
        component: 'DocumentHistoryService',
        operation: 'createVersion',
        retryCount: 0,
        maxRetries: 3
      });
    }
  }

  async compareVersions(documentId: string, version1: string, version2: string): Promise<any> {
    try {
      const response = await this.apiClient.get(
        `/documents/${documentId}/compare/${version1}/${version2}`
      );
      return response.data;
    } catch (error) {
      throw errorHandler.handleError(error, {
        component: 'DocumentHistoryService',
        operation: 'compareVersions',
        retryCount: 0,
        maxRetries: 3
      });
    }
  }

  private processHistoryResponse(data: any): DocumentHistory {
    return {
      documentId: data.documentId,
      versions: data.versions.map(this.processVersionEntry),
      totalVersions: data.versions.length,
      lastModified: new Date(data.lastModified)
    };
  }

  private processVersionEntry(version: any): HistoryEntry {
    return {
      versionId: version.id,
      timestamp: new Date(version.timestamp),
      author: version.author,
      changes: version.changes,
      metadata: version.metadata
    };
  }
}

export const documentHistoryService = new DocumentHistoryService();
