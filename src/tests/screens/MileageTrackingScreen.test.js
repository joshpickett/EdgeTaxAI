import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import * as Location from 'expo-location';
import MileageTrackingScreen from '../../screens/MileageTrackingScreen';

// Mock expo-location
jest.mock('expo-location');

describe('MileageTrackingScreen', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    Location.requestForegroundPermissionsAsync.mockResolvedValue({ status: 'granted' });
    Location.watchPositionAsync.mockImplementation((options, callback) => {
      callback({ coords: { latitude: 40.7128, longitude: -74.0060 } });
      return { remove: jest.fn() };
    });
  });

  it('renders correctly', () => {
    const { getByText, getByPlaceholderText } = render(<MileageTrackingScreen />);
    expect(getByText('Mileage Tracking')).toBeTruthy();
    expect(getByPlaceholderText('Start Location')).toBeTruthy();
    expect(getByPlaceholderText('End Location')).toBeTruthy();
  });

  it('handles location permission request', async () => {
    render(<MileageTrackingScreen />);
    await waitFor(() => {
      expect(Location.requestForegroundPermissionsAsync).toHaveBeenCalled();
    });
  });

  it('calculates distance correctly', async () => {
    const { getByText, getByPlaceholderText } = render(<MileageTrackingScreen />);
    
    fireEvent.changeText(getByPlaceholderText('Start Location'), 'New York');
    fireEvent.changeText(getByPlaceholderText('End Location'), 'Boston');
    fireEvent.press(getByText('Track Mileage'));

    await waitFor(() => {
      expect(getByText(/Distance:/)).toBeTruthy();
    });
  });

  it('handles GPS tracking toggle', async () => {
    const { getByText } = render(<MileageTrackingScreen />);
    
    const trackButton = getByText('Start GPS Tracking');
    fireEvent.press(trackButton);

    await waitFor(() => {
      expect(Location.watchPositionAsync).toHaveBeenCalled();
      expect(getByText('Stop GPS Tracking')).toBeTruthy();
    });
  });

  it('validates required fields', async () => {
    const { getByText } = render(<MileageTrackingScreen />);
    
    fireEvent.press(getByText('Track Mileage'));

    await waitFor(() => {
      expect(getByText('All fields are required.')).toBeTruthy();
    });
  });

  it('handles recurring trip settings', () => {
    const { getByText, getByPlaceholderText } = render(<MileageTrackingScreen />);
    
    fireEvent.press(getByText('Recurring Trip'));
    expect(getByPlaceholderText('Frequency (e.g., weekly, monthly)')).toBeTruthy();
  });

  it('handles location tracking errors', async () => {
    Location.requestForegroundPermissionsAsync.mockRejectedValue(new Error('Permission denied'));
    
    const { getByText } = render(<MileageTrackingScreen />);
    fireEvent.press(getByText('Start GPS Tracking'));

    await waitFor(() => {
      expect(getByText('Failed to start location tracking')).toBeTruthy();
    });
  });

  it('calculates tax deduction', async () => {
    const { getByText, getByPlaceholderText } = render(<MileageTrackingScreen />);
    
    fireEvent.changeText(getByPlaceholderText('Start Location'), 'New York');
    fireEvent.changeText(getByPlaceholderText('End Location'), 'Boston');
    fireEvent.press(getByText('Track Mileage'));

    await waitFor(() => {
      expect(getByText(/Estimated Tax Deduction/)).toBeTruthy();
    });
  });
});
