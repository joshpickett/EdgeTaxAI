import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import { Alert, Linking } from 'react-native';
import ProfileScreen from '../../screens/ProfileScreen';
import { getProfile, updateProfile } from '../../services/authService';

jest.mock('../../services/authService');
jest.mock('react-native/Libraries/Linking/Linking', () => ({
  openURL: jest.fn(),
}));

describe('ProfileScreen', () => {
  const mockProfile = {
    full_name: 'John Doe',
    email: 'john@example.com',
    phone_number: '1234567890'
  };

  beforeEach(() => {
    jest.clearAllMocks();
    getProfile.mockResolvedValue(mockProfile);
    Alert.alert = jest.fn();
  });

  it('renders loading state initially', () => {
    const { getByTestId } = render(<ProfileScreen />);
    expect(getByTestId('loading-indicator')).toBeTruthy();
  });

  it('loads and displays profile data', async () => {
    const { getByPlaceholderText } = render(<ProfileScreen />);
    
    await waitFor(() => {
      expect(getByPlaceholderText('Full Name').props.value).toBe('John Doe');
      expect(getByPlaceholderText('Email').props.value).toBe('john@example.com');
      expect(getByPlaceholderText('Phone Number').props.value).toBe('1234567890');
    });
  });

  it('handles profile update successfully', async () => {
    updateProfile.mockResolvedValue({ success: true });
    
    const { getByText, getByPlaceholderText } = render(<ProfileScreen />);
    
    await waitFor(() => {
      fireEvent.changeText(getByPlaceholderText('Full Name'), 'Jane Doe');
      fireEvent.press(getByText('Update Profile'));
    });

    expect(updateProfile).toHaveBeenCalledWith(
      expect.objectContaining({ full_name: 'Jane Doe' })
    );
    expect(Alert.alert).toHaveBeenCalledWith('Success', 'Profile updated successfully!');
  });

  it('validates required fields before update', async () => {
    const { getByText, getByPlaceholderText } = render(<ProfileScreen />);
    
    await waitFor(() => {
      fireEvent.changeText(getByPlaceholderText('Full Name'), '');
      fireEvent.press(getByText('Update Profile'));
    });

    expect(Alert.alert).toHaveBeenCalledWith('Error', expect.any(String));
  });

  it('handles platform connection attempts', async () => {
    const { getByText } = render(<ProfileScreen />);
    
    fireEvent.press(getByText('Connect Uber'));
    
    expect(Linking.openURL).toHaveBeenCalledWith(
      expect.stringContaining('uber')
    );
  });

  it('handles API errors gracefully', async () => {
    getProfile.mockRejectedValue(new Error('API Error'));
    
    render(<ProfileScreen />);
    
    await waitFor(() => {
      expect(Alert.alert).toHaveBeenCalledWith('Error', 'Failed to fetch profile details.');
    });
  });
});
