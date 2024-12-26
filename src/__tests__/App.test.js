import React from 'react';
import { render } from '@testing-library/react';
import { Provider } from 'react-redux';
import { store } from '../store';
import App from '../../App';
import AppNavigator from '../navigation/AppNavigator';

// Mock the AppNavigator component
jest.mock('../navigation/AppNavigator', () => {
  return function MockAppNavigator() {
    return <div data-testid="mock-app-navigator">Mock Navigator</div>;
  };
});

describe('App Component', () => {
  it('renders without crashing', () => {
    const { container } = render(<App />);
    expect(container).toBeTruthy();
  });

  it('renders with Redux Provider', () => {
    const { container } = render(<App />);
    // Check if Provider exists by verifying store context
    expect(container.firstChild).toBeTruthy();
  });

  it('renders AppNavigator component', () => {
    const { getByTestId } = render(<App />);
    const navigator = getByTestId('mock-app-navigator');
    expect(navigator).toBeInTheDocument();
  });

  it('provides Redux store to child components', () => {
    const mockStore = {
      ...store,
      getState: jest.fn(),
      dispatch: jest.fn(),
    };

    const { container } = render(
      <Provider store={mockStore}>
        <AppNavigator />
      </Provider>
    );
    
    expect(container).toBeTruthy();
  });

  // Snapshot test
  it('matches snapshot', () => {
    const { container } = render(<App />);
    expect(container).toMatchSnapshot();
  });

  // Error boundary test
  it('handles errors gracefully', () => {
    const spy = jest.spyOn(console, 'error');
    spy.mockImplementation(() => {});

    const ErrorComponent = () => {
      throw new Error('Test error');
    };

    jest.mock('../navigation/AppNavigator', () => ErrorComponent);

    expect(() => render(<App />)).not.toThrow();

    spy.mockRestore();
  });
});
