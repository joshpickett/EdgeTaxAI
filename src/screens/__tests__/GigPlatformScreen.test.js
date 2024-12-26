import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import GigPlatformScreen from '../GigPlatformScreen';
import { 
  fetchPlatformData, 
  fetchConnectedPlatforms, 
  syncPlatformData 
} from '../../services/gigPlatformService';
import * as Linking from 'react-native/Libraries/Linking/Linking';

jest.mock('../../services/gigPlatformService');
jest.mock('react-native/Libraries/Linking/Linking', () => ({
  openURL: jest.fn()
}));

describe('GigPlatformScreen', () => {
  beforeEach(() => {
    fetchPlatformData.mockClear();
    fetchConnectedPlatforms.mockClear();
    syncPlatformData.mockClear();
  });

  it('renders platform connection options', () => {
    const { getByText } = render(<GigPlatformScreen />);
    
    expect(getByText('Manage Gig Platforms')).toBeTruthy();
    expect(getByText('Connect Uber')).toBeTruthy();
    expect(getByText('Connect Lyft')).toBeTruthy();
    expect(getByText('Connect DoorDash')).toBeTruthy();
  });

  it('handles OAuth platform connection', async () => {
    const { getByText } = render(<GigPlatformScreen />);
    
    fireEvent.press(getByText('Connect Uber'));
    
    await waitFor(() => {
      expect(Linking.openURL).toHaveBeenCalledWith(
        expect.stringContaining('/api/gig/connect/uber')
      );
    });
  });

  it('handles API key platform connection', async () => {
    const { getByText, getByPlaceholderText } = render(<GigPlatformScreen />);
    
    fireEvent.changeText(
      getByPlaceholderText('Enter DoorDash API Key'),
      'test-api-key'
    );
    fireEvent.press(getByText('Connect DoorDash'));

    await waitFor(() => {
      expect(connectApiKeyPlatform).toHaveBeenCalledWith(
        'doordash',
        'test-api-key'
      );
    });
  });

  it('loads connected platforms', async () => {
    const mockPlatforms = [
      { platform: 'uber', status: 'connected' }
    ];
    fetchConnectedPlatforms.mockResolvedValueOnce(mockPlatforms);

    const { getByText, findByText } = render(<GigPlatformScreen />);
    
    fireEvent.press(getByText('Load Connected Platforms'));

    expect(await findByText('UBER')).toBeTruthy();
  });

  it('handles platform sync', async () => {
    const { getByText } = render(<GigPlatformScreen />);
    
    fireEvent.press(getByText('Sync'));

    await waitFor(() => {
      expect(syncPlatformData).toHaveBeenCalled();
    });
  });

  it('handles sync errors with retry', async () => {
    syncPlatformData.mockRejectedValueOnce(new Error('Sync failed'));
    
    const { getByText } = render(<GigPlatformScreen />);
    
    fireEvent.press(getByText('Sync'));

    await waitFor(() => {
      expect(syncPlatformData).toHaveBeenCalledTimes(1);
    });
  });
});
