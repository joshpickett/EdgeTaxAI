import ReceiptService from '../receiptService';
import { apiClient } from '../apiClient';
import config from '../../config';

jest.mock('../apiClient');

describe('ReceiptService', () => {
    beforeEach(() => {
        jest.clearAllMocks();
    });

    describe('processReceipt', () => {
        const mockFile = new File([''], 'receipt.jpg', { type: 'image/jpeg' });

        test('should process receipt successfully', async () => {
            const mockResponse = {
                data: {
                    items: [{ description: 'Office Supplies', amount: 50.00 }],
                    total: 50.00,
                    date: '2023-01-01'
                }
            };
            apiClient.post.mockResolvedValueOnce(mockResponse);

            const result = await ReceiptService.processReceipt(mockFile);
            expect(result).toEqual(mockResponse.data);
            expect(apiClient.post).toHaveBeenCalledWith(
                '/expenses/process-receipt',
                expect.any(FormData),
                expect.any(Object)
            );
        });

        test('should handle processing errors', async () => {
            const error = new Error('Processing failed');
            apiClient.post.mockRejectedValueOnce(error);

            await expect(
                ReceiptService.processReceipt(mockFile)
            ).rejects.toThrow('Processing failed');
        });
    });

    describe('analyzeReceipt', () => {
        const mockReceiptData = {
            image: 'base64_encoded_image',
            metadata: { source: 'mobile_camera' }
        };

        test('should analyze receipt successfully', async () => {
            const mockResponse = {
                data: {
                    category: 'office_supplies',
                    tax_deductible: true,
                    confidence: 0.95
                }
            };
            apiClient.post.mockResolvedValueOnce(mockResponse);

            const result = await ReceiptService.analyzeReceipt(mockReceiptData);
            expect(result).toEqual(mockResponse.data);
        });

        test('should handle analysis errors', async () => {
            apiClient.post.mockRejectedValueOnce(new Error('Analysis failed'));

            await expect(
                ReceiptService.analyzeReceipt(mockReceiptData)
            ).rejects.toThrow('Analysis failed');
        });
    });
});
