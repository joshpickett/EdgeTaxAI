import React, { useState, useEffect } from 'react';
import { View, Platform } from 'react-native';
import { StreamlinedTaxWizard } from '../components/StreamlinedTaxWizard/StreamlinedTaxWizard';
import { DocumentManager } from '../components/DocumentCollection/DocumentManager';
import { COLORS } from '../assets/config/colors';
import { SPACING } from '../assets/config/spacing';

interface UnifiedDashboardProps {
  userId: string;
  onLogout: () => void;
}

export const UnifiedDashboard: React.FC<UnifiedDashboardProps> = ({
  userId,
  onLogout
}) => {
  const [isOnboarded, setIsOnboarded] = useState(false);
  const [documents, setDocuments] = useState([]);

  useEffect(() => {
    checkOnboardingStatus();
    fetchDocuments();
  }, [userId]);

  const checkOnboardingStatus = async () => {
    // Check if user has completed onboarding
    try {
      const response = await fetch(`/api/users/${userId}/onboarding-status`);
      const data = await response.json();
      setIsOnboarded(data.isComplete);
    } catch (error) {
      console.error('Error checking onboarding status:', error);
    }
  };

  const fetchDocuments = async () => {
    try {
      const response = await fetch(`/api/users/${userId}/documents`);
      const data = await response.json();
      setDocuments(data.documents);
    } catch (error) {
      console.error('Error fetching documents:', error);
    }
  };

  const handleOnboardingComplete = () => {
    setIsOnboarded(true);
  };

  return (
    <View style={styles.container}>
      {!isOnboarded ? (
        <StreamlinedTaxWizard
          userId={userId}
          onComplete={handleOnboardingComplete}
        />
      ) : (
        <DocumentManager
          userId={userId}
          documents={documents}
          onDocumentsUpdate={fetchDocuments}
        />
      )}
    </View>
  );
};

const styles = {
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
    padding: Platform.OS === 'web' ? SPACING.xl : SPACING.md,
  }
};
