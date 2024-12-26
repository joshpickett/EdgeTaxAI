import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import ProfileScreen from '../ProfileScreen';
import { getProfile, updateProfile } from '../../services/authService';
import * as ImagePicker from 'expo-image-picker';
import { Linking } from 'react-native';

jest.mock('../../services/authService');
jest.mock('expo-image-picker');
jest.mock('react-native/Libraries/Linking/Linking', () => ({
  openURL: jest.fn()
}));

describe('ProfileScreen', () => {
  const mockProfile = {
    full_name: 'Test User',
    email: 'test@example.com',
    phone_number: '1234567890'
  };

  beforeEach(() => {
    getProfile.mockResolvedValue(mockProfile);
    updateProfile.mockResolvedValue({ success: true });
  });

  it('renders profile data correctly', async () => {
    const { getByPlaceholderText } = render(<ProfileScreen />);

    await waitFor(() => {
      expect(getByPlaceholderText('Full Name').props.value).toBe('Test User');
      expect(getByPlaceholderText('Email').props.value).toBe('test@example.com');
      expect(getByPlaceholderText('Phone Number').props.value).toBe('1234567890');
    });
  });

  it('handles profile update', async () => {
    const { getByText, getByPlaceholderText } = render(<ProfileScreen />);

    await waitFor(() => {
      fireEvent.changeText(getByPlaceholderText('Full Name'), 'Updated Name');
      fireEvent.press(getByText('Update Profile'));
    });

    expect(updateProfile).toHaveBeenCalledWith(
      'Updated Name',
      'test@example.com',
      '1234567890'
    );
  });

  it('handles validation errors', async () => {
    const { getByText } = render(<ProfileScreen />);

    await waitFor(() => {
      fireEvent.changeText(getByPlaceholderText('Full Name'), '');
      fireEvent.press(getByText('Update Profile'));
    });

    expect(getByText('Name is required')).toBeTruthy();
  });

  it('handles platform connection', async () => {
    const { getByText } = render(<ProfileScreen />);

    fireEvent.press(getByText('Connect Uber'));

    expect(Linking.openURL).toHaveBeenCalledWith(
      expect.stringContaining('/api/gig/connect/uber')
    );
  });

  it('handles profile image update', async () => {
    ImagePicker.launchImageLibraryAsync.mockResolvedValueOnce({
      cancelled: false,
      uri: 'test-uri'
    });

    const { getByText } = render(<ProfileScreen />);
    
    await waitFor(() => {
      fireEvent.press(getByText('Update Profile Image'));
    });

    expect(ImagePicker.launchImageLibraryAsync).toHaveBeenCalled();
  });
});
