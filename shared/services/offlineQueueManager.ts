import { QueueOperation, QueueItem, ProcessingResult } from '../types/queue';
import { StorageManager } from './storageManager';

export class OfflineQueueManager {
    private queue: QueueItem[] = [];
    private storageManager: StorageManager;
    private isProcessing: boolean = false;
    private readonly MAX_RETRIES = 3;
    private readonly RETRY_DELAY = 1000;

    constructor() {
        this.storageManager = new StorageManager();
        this.initializeQueue();
    }

    private async initializeQueue(): Promise<void> {
        try {
            const savedQueue = await this.storageManager.getItem('operationQueue');
            if (savedQueue) {
                this.queue = JSON.parse(savedQueue);
            }
        } catch (error) {
            console.error('Error initializing queue:', error);
        }
    }

    async addToQueue(operation: string, params: any): Promise<void> {
        const queueItem: QueueItem = {
            id: `${operation}_${Date.now()}`,
            operation,
            params,
            timestamp: Date.now(),
            retryCount: 0,
            status: 'pending'
        };

        this.queue.push(queueItem);
        await this.persistQueue();
    }

    async processQueue(): Promise<ProcessingResult[]> {
        if (this.isProcessing || !navigator.onLine) {
            return [];
        }

        this.isProcessing = true;
        const results: ProcessingResult[] = [];

        try {
            for (const item of this.queue) {
                if (item.status === 'completed') continue;

                const result = await this.processItem(item);
                results.push(result);

                if (result.success) {
                    item.status = 'completed';
                } else if (item.retryCount >= this.MAX_RETRIES) {
                    item.status = 'failed';
                }
            }

            this.queue = this.queue.filter(item => item.status !== 'completed');
            await this.persistQueue();

        } catch (error) {
            console.error('Error processing queue:', error);
        } finally {
            this.isProcessing = false;
        }

        return results;
    }

    private async processItem(item: QueueItem): Promise<ProcessingResult> {
        try {
            const result = await this.executeOperation(item);
            return {
                id: item.id,
                success: true,
                result
            };
        } catch (error) {
            item.retryCount++;
            return {
                id: item.id,
                success: false,
                error: error.message
            };
        }
    }

    private async executeOperation(item: QueueItem): Promise<any> {
        switch (item.operation) {
            case 'processDocument':
                return await this.processDocument(item.params);
            case 'verifyField':
                return await this.verifyField(item.params);
            default:
                throw new Error(`Unknown operation: ${item.operation}`);
        }
    }

    private async persistQueue(): Promise<void> {
        try {
            await this.storageManager.setItem('operationQueue', JSON.stringify(this.queue));
        } catch (error) {
            console.error('Error persisting queue:', error);
        }
    }

    async getQueueStatus(): Promise<{
        pending: number;
        completed: number;
        failed: number;
    }> {
        return {
            pending: this.queue.filter(item => item.status === 'pending').length,
            completed: this.queue.filter(item => item.status === 'completed').length,
            failed: this.queue.filter(item => item.status === 'failed').length
        };
    }

    async clearQueue(): Promise<void> {
        this.queue = [];
        await this.persistQueue();
    }
}
