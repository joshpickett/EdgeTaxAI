import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import GigPlatformScreen from '../../screens/GigPlatformScreen';
import { 
  fetchPlatformData, 
  fetchConnectedPlatforms, 
  syncPlatformData, 
  connectApiKeyPlatform 
} from '../../services/gigPlatformService';

// Mock the gigPlatformService
jest.mock('../../services/gigPlatformService');

describe('GigPlatformScreen', () => {
  const mockPlatforms = [
    { name: 'Uber', key: 'uber', connected: false },
    { name: 'Lyft', key: 'lyft', connected: true },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    fetchConnectedPlatforms.mockResolvedValue(mockPlatforms);
    fetchPlatformData.mockResolvedValue([]);
    syncPlatformData.mockResolvedValue({ success: true });
    connectApiKeyPlatform.mockResolvedValue({ success: true });
  });

  it('renders correctly', () => {
    const { getByText, getAllByText } = render(<GigPlatformScreen />);
    expect(getByText('Manage Gig Platforms')).toBeTruthy();
    expect(getAllByText(/Connect/).length).toBeGreaterThan(0);
  });

  it('handles platform connection with API key', async () => {
    const { getByPlaceholderText, getByText } = render(<GigPlatformScreen />);
    
    fireEvent.changeText(getByPlaceholderText('Enter API Key'), 'test-api-key');
    fireEvent.press(getByText('Connect DoorDash'));

    await waitFor(() => {
      expect(connectApiKeyPlatform).toHaveBeenCalledWith(
        'doordash',
        'test-api-key'
      );
    });
  });

  it('handles platform synchronization', async () => {
    const { getByText } = render(<GigPlatformScreen />);
    
    fireEvent.press(getByText('Sync Lyft'));

    await waitFor(() => {
      expect(syncPlatformData).toHaveBeenCalledWith('lyft', expect.any(String));
    });
  });

  it('displays loading state', async () => {
    fetchPlatformData.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));
    
    const { getByTestId } = render(<GigPlatformScreen />);
    fireEvent.press(getByTestId('fetch-data-button'));
    
    expect(getByTestId('loading-indicator')).toBeTruthy();
  });

  it('handles errors appropriately', async () => {
    fetchPlatformData.mockRejectedValue(new Error('API Error'));
    
    const { getByText } = render(<GigPlatformScreen />);
    fireEvent.press(getByText('Fetch Platform Data'));

    await waitFor(() => {
      expect(getByText('Failed to fetch platform data')).toBeTruthy();
    });
  });

  it('displays connected platforms', async () => {
    const { getByText } = render(<GigPlatformScreen />);
    
    await waitFor(() => {
      expect(getByText('Lyft (Connected)')).toBeTruthy();
    });
  });

  it('handles retry logic for failed connections', async () => {
    connectApiKeyPlatform.mockRejectedValueOnce(new Error('Connection failed'));
    connectApiKeyPlatform.mockResolvedValueOnce({ success: true });

    const { getByText, getByPlaceholderText } = render(<GigPlatformScreen />);
    
    fireEvent.changeText(getByPlaceholderText('Enter API Key'), 'test-api-key');
    fireEvent.press(getByText('Connect DoorDash'));

    await waitFor(() => {
      expect(connectApiKeyPlatform).toHaveBeenCalledTimes(2);
    });
  });
});
