import { apiClient } from './apiClient';

export const processReceipt = async (imageUri) => {
  try {
    const formData = new FormData();
    formData.append('receipt', {
      uri: imageUri,
      type: 'image/jpeg',
      name: 'receipt.jpg',
    });

    const response = await fetch('http://localhost:5000/api/process-receipt', {
      method: 'POST',
      body: formData,
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    if (!response.ok) {
      throw new Error('Failed to process receipt');
    }

    const data = await response.json();
    return {
      description: data.text,
      amount: data.amount,
      category: data.category,
      expense_id: data.expense_id,
      document_id: data.document_id
    };
  } catch (error) {
    console.error('Receipt processing error:', error);
    throw error;
  }
};
