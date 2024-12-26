import ExpenseService from '../expenseService';
import ApiClient from '../apiClient';
import config from '../../config';
import { handleApiError } from '../../utils/errorHandler';

jest.mock('../apiClient');
jest.mock('../../utils/errorHandler');

describe('ExpenseService', () => {
    let expenseService;

    beforeEach(() => {
        expenseService = new ExpenseService();
        jest.clearAllMocks();
    });

    describe('createPlatformExpense', () => {
        const mockExpenseData = {
            amount: 100,
            description: 'Test expense',
            date: '2023-01-01'
        };

        test('should create platform expense successfully', async () => {
            ApiClient.post.mockResolvedValueOnce({
                data: { id: '123', ...mockExpenseData }
            });

            const result = await expenseService.createPlatformExpense(
                mockExpenseData,
                'uber'
            );
            expect(result.id).toBe('123');
        });

        test('should handle platform-specific errors', async () => {
            const error = new Error('Platform error');
            ApiClient.post.mockRejectedValueOnce(error);
            handleApiError.mockImplementationOnce(err => { throw err; });

            await expect(
                expenseService.createPlatformExpense(mockExpenseData, 'uber')
            ).rejects.toThrow('Platform error');
        });
    });

    describe('processReceipt', () => {
        test('should process receipt file successfully', async () => {
            const mockFile = new File([''], 'receipt.jpg');
            ApiClient.post.mockResolvedValueOnce({
                data: {
                    amount: 50,
                    description: 'Office supplies'
                }
            });

            const result = await expenseService.processReceipt(mockFile);
            expect(result.amount).toBe(50);
        });

        test('should handle Optical Character Recognition confidence threshold', async () => {
            const mockFile = new File([''], 'receipt.jpg');
            ApiClient.post.mockImplementation((url, data, configuration) => {
                expect(configuration.headers['X-OCR-Confidence-Threshold'])
                    .toBe(configuration.ocr.confidenceThreshold);
                return Promise.resolve({ data: {} });
            });

            await expenseService.processReceipt(mockFile);
        });
    });
});
