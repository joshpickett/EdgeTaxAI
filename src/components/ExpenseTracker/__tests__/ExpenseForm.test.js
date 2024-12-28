import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import { setupSrcPath } from '../../../setup_path';
import { Provider } from 'react-redux';
import { colors, typography } from '../../../styles/tokens';
import configureStore from 'redux-mock-store';
import ExpenseForm from '../ExpenseForm';

const mockStore = configureStore([]);

describe('ExpenseForm', () => {
  let store;
  let component;

  beforeEach(() => {
    store = mockStore({
      expenses: {
        loading: false,
        error: null
      }
    });

    component = render(
      <Provider store={store}>
        <ExpenseForm onSubmit={jest.fn()} />
      </Provider>
    );
  });

  it('renders correctly', () => {
    expect(component).toBeTruthy();
    expect(component.getByPlaceholderText('Description')).toBeTruthy();
    expect(component.getByPlaceholderText('Amount')).toBeTruthy();
    expect(component.getByPlaceholderText('Category (optional)')).toBeTruthy();
  });

  it('validates required fields', async () => {
    const addButton = component.getByText('Add Expense');
    fireEvent.press(addButton);

    await waitFor(() => {
      const errorMessage = component.getByText('Description is required');
      expect(errorMessage.props.style.color).toBe(colors.error.main);
    });
  });

  it('submits form with valid data', async () => {
    const descriptionInput = component.getByPlaceholderText('Description');
    const amountInput = component.getByPlaceholderText('Amount');
    
    fireEvent.changeText(descriptionInput, 'Test Expense');
    fireEvent.changeText(amountInput, '50.00');
    
    const addButton = component.getByText('Add Expense');
    fireEvent.press(addButton);

    const actions = store.getActions();
    expect(actions[0].type).toBe('expenses/add/pending');
  });
});
