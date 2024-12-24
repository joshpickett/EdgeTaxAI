import '@testing-library/jest-native/extend-expect';
import { jest } from '@jest/globals';

// Mock navigation
jest.mock('@react-navigation/native', () => ({
  useNavigation: () => ({
    navigate: jest.fn(),
    goBack: jest.fn(),
  }),
}));

// Mock redux
jest.mock('react-redux', () => ({
  useDispatch: () => jest.fn(),
  useSelector: jest.fn(),
}));

// Mock services
jest.mock('../services/expenseService');
jest.mock('../services/bankService');
jest.mock('../services/taxService');
jest.mock('../services/authService');
