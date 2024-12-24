class ExpenseService {
    constructor() {
        this.client = ApiClient;
    }

    // Add platform-specific expense handling
    async createPlatformExpense(expenseData, platform) {
        try {
            const response = await this.client.post('/expenses/platform', expenseData, {
                platform,
                platformVersion: config.platforms[platform].version
            });
            return response.data;
        } catch (error) {
            throw handleApiError(error);
        }
    }

    async processReceipt(receiptFile) {
        try {
            const formData = new FormData();
            formData.append('receipt', receiptFile);
            
            // Add Optical Character Recognition confidence score handling
            const response = await this.client.post('/expenses/process-receipt', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                    'X-OCR-Confidence-Threshold': config.ocr.confidenceThreshold
                }
            });

            // ...rest of the code...
        } catch (error) {
            throw handleApiError(error);
        }
    }

    // ...rest of the code...
}
