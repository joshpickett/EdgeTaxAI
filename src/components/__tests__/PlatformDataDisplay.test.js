import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import { setupSrcPath } from '../../setup_path';
import PlatformDataDisplay from '../PlatformDataDisplay';
import { colors, typography } from '../../styles/tokens';

describe('PlatformDataDisplay', () => {
  const mockData = {
    uber: {
      earnings: 1000,
      trips: 50,
      hours: 20
    },
    lyft: {
      earnings: 800,
      trips: 40,
      hours: 15
    }
  };

  it('renders platform data correctly', () => {
    const { getByText } = render(
      <PlatformDataDisplay data={mockData} />
    );
    const platformTitle = getByText('Uber');
    expect(platformTitle.props.style).toContainEqual(
      expect.objectContaining({ fontSize: typography.fontSize.lg }));

    expect(getByText('$1,000')).toBeTruthy();
    expect(getByText('50 trips')).toBeTruthy();
    expect(getByText('20 hours')).toBeTruthy();

    expect(getByText('Lyft')).toBeTruthy();
    expect(getByText('$800')).toBeTruthy();
    expect(getByText('40 trips')).toBeTruthy();
    expect(getByText('15 hours')).toBeTruthy();
  });

  it('handles empty data', () => {
    const { getByText } = render(
      <PlatformDataDisplay data={{}} />
    );

    expect(getByText('No platform data available')).toBeTruthy();
  });

  it('handles platform selection', () => {
    const onSelectPlatform = jest.fn();
    const { getByText } = render(
      <PlatformDataDisplay 
        data={mockData} 
        onSelectPlatform={onSelectPlatform}
      />
    );

    fireEvent.press(getByText('Uber'));
    expect(onSelectPlatform).toHaveBeenCalledWith('uber');
  });

  it('displays loading state', () => {
    const { getByTestId } = render(
      <PlatformDataDisplay data={mockData} loading={true} />
    );

    expect(getByTestId('loading-indicator')).toBeTruthy();
  });

  it('handles error state', () => {
    const { getByText } = render(
      <PlatformDataDisplay 
        data={mockData} 
        error="Failed to load platform data" 
      />
    );

    expect(getByText('Failed to load platform data')).toBeTruthy();
  });
});
