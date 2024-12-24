import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import AddExpenseScreen from '../../screens/expenses/AddExpenseScreen';
import * as DocumentPicker from 'expo-document-picker';
import { addExpense, categorizeExpense } from '../../services/expenseService';

// Mock the dependencies
jest.mock('../../services/expenseService');
jest.mock('expo-document-picker');

describe('AddExpenseScreen', () => {
    const mockNavigation = {
        goBack: jest.fn()
    };

    beforeEach(() => {
        jest.clearAllMocks();
    });

    test('renders correctly', () => {
        const { getByPlaceholderText, getByText } = render(
            <AddExpenseScreen navigation={mockNavigation} />
        );

        expect(getByPlaceholderText('Description')).toBeTruthy();
        expect(getByPlaceholderText('Amount')).toBeTruthy();
        expect(getByText('Add Expense')).toBeTruthy();
    });

    test('handles expense addition successfully', async () => {
        addExpense.mockResolvedValueOnce({ success: true });

        const { getByPlaceholderText, getByText } = render(
            <AddExpenseScreen navigation={mockNavigation} />
        );

        fireEvent.changeText(getByPlaceholderText('Description'), 'Test Expense');
        fireEvent.changeText(getByPlaceholderText('Amount'), '100');
        fireEvent.changeText(getByPlaceholderText('Category'), 'Food');
        fireEvent.changeText(getByPlaceholderText('Date (YYYY-MM-DD)'), '2023-01-01');

        fireEvent.press(getByText('Add Expense'));

        await waitFor(() => {
            expect(addExpense).toHaveBeenCalledWith(
                'Test Expense',
                '100',
                'Food',
                '2023-01-01'
            );
            expect(mockNavigation.goBack).toHaveBeenCalled();
        });
    });

    test('handles auto-categorization', async () => {
        categorizeExpense.mockResolvedValueOnce('Food');

        const { getByPlaceholderText } = render(
            <AddExpenseScreen navigation={mockNavigation} />
        );

        const descriptionInput = getByPlaceholderText('Description');
        fireEvent.changeText(descriptionInput, 'lunch');
        fireEvent(descriptionInput, 'blur');

        await waitFor(() => {
            expect(categorizeExpense).toHaveBeenCalledWith('lunch');
        });
    });

    test('handles receipt upload', async () => {
        DocumentPicker.getDocumentAsync.mockResolvedValueOnce({
            type: 'success',
            uri: 'test-uri'
        });

        const { getByText } = render(
            <AddExpenseScreen navigation={mockNavigation} />
        );

        fireEvent.press(getByText('Upload Receipt'));

        await waitFor(() => {
            expect(DocumentPicker.getDocumentAsync).toHaveBeenCalled();
        });
    });

    test('validates required fields', async () => {
        const { getByText } = render(
            <AddExpenseScreen navigation={mockNavigation} />
        );

        fireEvent.press(getByText('Add Expense'));

        await waitFor(() => {
            expect(addExpense).not.toHaveBeenCalled();
        });
    });

    test('handles Optical Character Recognition processing error', async () => {
        DocumentPicker.getDocumentAsync.mockResolvedValueOnce({
            type: 'success',
            uri: 'test-uri'
        });

        global.fetch = jest.fn(() =>
            Promise.reject(new Error('Optical Character Recognition processing failed'))
        );

        const { getByText } = render(
            <AddExpenseScreen navigation={mockNavigation} />
        );

        fireEvent.press(getByText('Upload Receipt'));

        await waitFor(() => {
            expect(DocumentPicker.getDocumentAsync).toHaveBeenCalled();
        });
    });
});
