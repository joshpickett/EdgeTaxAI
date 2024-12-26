import { OfflineQueueManager } from '../offlineQueueManager';
import { TaxCalculation, QuarterlyEstimate } from '../../types/tax';

describe('OfflineQueueManager', () => {
    let queueManager: OfflineQueueManager;

    beforeEach(() => {
        queueManager = new OfflineQueueManager();
        localStorage.clear();
        jest.clearAllMocks();
    });

    describe('addToQueue', () => {
        test('should add operation to queue', async () => {
            const operation = 'calculateTax';
            const params = { income: 1000 };

            await queueManager.addToQueue(operation, params);
            
            const queue = JSON.parse(localStorage.getItem('taxOperationQueue') || '[]');
            expect(queue).toHaveLength(1);
            expect(queue[0].operation).toBe(operation);
            expect(queue[0].params).toEqual(params);
        });
    });

    describe('processQueue', () => {
        beforeEach(() => {
            // Mock navigator.onLine
            Object.defineProperty(navigator, 'onLine', {
                configurable: true,
                value: true
            });
        });

        test('should not process queue when offline', async () => {
            Object.defineProperty(navigator, 'onLine', {
                configurable: true,
                value: false
            });

            await queueManager.addToQueue('calculateTax', { income: 1000 });
            await queueManager.processQueue();

            const queue = JSON.parse(localStorage.getItem('taxOperationQueue') || '[]');
            expect(queue).toHaveLength(1);
        });

        test('should process queue items successfully', async () => {
            const mockTaxService = {
                calculateQuarterlyTax: jest.fn().mockResolvedValue({}),
                updateDeductions: jest.fn().mockResolvedValue({})
            };

            await queueManager.addToQueue('calculateTax', { income: 1000 });
            await queueManager.processQueue();

            const queue = JSON.parse(localStorage.getItem('taxOperationQueue') || '[]');
            expect(queue).toHaveLength(0);
        });

        test('should handle unknown operations', async () => {
            await queueManager.addToQueue('unknownOperation', {});
            
            await expect(queueManager.processQueue())
                .rejects
                .toThrow('Unknown operation: unknownOperation');
        });
    });
});
