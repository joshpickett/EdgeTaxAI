import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import * as Location from 'expo-location';
import MileageTrackingScreen from '../MileageTrackingScreen';
import mileageService from '../../services/mileageService';

jest.mock('expo-location');
jest.mock('../../services/mileageService');
jest.mock('@react-native-community/datetimepicker', () => 'DateTimePicker');

describe('MileageTrackingScreen', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    Location.requestForegroundPermissionsAsync.mockResolvedValue({ status: 'granted' });
    Location.watchPositionAsync.mockImplementation((options, callback) => {
      callback({ coords: { latitude: 1, longitude: 1 } });
      return { remove: jest.fn() };
    });
  });

  it('renders correctly', () => {
    const { getByText, getByPlaceholderText } = render(<MileageTrackingScreen />);
    
    expect(getByText('Mileage Tracking')).toBeTruthy();
    expect(getByPlaceholderText('Start Location')).toBeTruthy();
    expect(getByPlaceholderText('End Location')).toBeTruthy();
    expect(getByPlaceholderText('Business Purpose')).toBeTruthy();
  });

  it('handles mileage calculation', async () => {
    mileageService.calculateMileage.mockResolvedValueOnce({
      distance: '10.5',
      tax_deduction: 5.25
    });

    const { getByText, getByPlaceholderText } = render(<MileageTrackingScreen />);

    fireEvent.changeText(getByPlaceholderText('Start Location'), 'Start');
    fireEvent.changeText(getByPlaceholderText('End Location'), 'End');
    fireEvent.changeText(getByPlaceholderText('Business Purpose'), 'Meeting');
    
    fireEvent.press(getByText('Track Mileage'));

    await waitFor(() => {
      expect(getByText('Distance: 10.5')).toBeTruthy();
      expect(getByText('Estimated Tax Deduction: $5.25')).toBeTruthy();
    });
  });

  it('handles GPS tracking', async () => {
    const { getByText } = render(<MileageTrackingScreen />);
    
    await waitFor(() => {
      expect(Location.requestForegroundPermissionsAsync).toHaveBeenCalled();
      expect(Location.watchPositionAsync).toHaveBeenCalled();
    });
  });

  it('handles validation errors', async () => {
    const { getByText } = render(<MileageTrackingScreen />);
    
    fireEvent.press(getByText('Track Mileage'));

    await waitFor(() => {
      expect(getByText('Error')).toBeTruthy();
    });
  });

  it('handles recurring trips', () => {
    const { getByText, getByPlaceholderText } = render(<MileageTrackingScreen />);
    
    fireEvent.valueChange(getByText('Recurring Trip'), true);
    
    expect(getByPlaceholderText('Frequency (e.g., weekly, monthly)')).toBeTruthy();
  });
});
