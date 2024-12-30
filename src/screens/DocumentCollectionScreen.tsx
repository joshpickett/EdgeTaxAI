import React, { useState } from 'react';
import { View, ScrollView, StyleSheet } from 'react-native';
import { Text, Card, Button, List, Chip } from 'react-native-paper';
import { MobileFormScreen } from '../components/mobile/MobileFormScreen';
import { DocumentUploader } from '../components/DocumentUploader';
import { COLORS } from '../../assets/config/colors';
import { SPACING } from '../../assets/config/spacing';

const REQUIRED_DOCUMENTS = [
  {
    id: 'w2',
    title: 'W-2 Forms',
    description: 'Wage and Tax Statement from employers',
    required: true
  },
  {
    id: '1099-nec',
    title: '1099-NEC Forms',
    description: 'Nonemployee Compensation from gig platforms',
    required: true
  },
  {
    id: '1099-k',
    title: '1099-K Forms',
    description: 'Payment Card and Third Party Network Transactions',
    required: true
  },
  {
    id: 'expenses',
    title: 'Expense Receipts',
    description: 'Business-related expense documentation',
    required: false
  }
];

export const DocumentCollectionScreen = ({ navigation }) => {
  const [uploadedDocs, setUploadedDocs] = useState<{[key: string]: any}>({});
  const [processing, setProcessing] = useState<{[key: string]: boolean}>({});

  const handleDocumentUpload = async (docType: string, file: any) => {
    setProcessing(prev => ({ ...prev, [docType]: true }));
    try {
      // Process document with Optical Character Recognition
      const processedDoc = await processDocument(file);
      setUploadedDocs(prev => ({
        ...prev,
        [docType]: [...(prev[docType] || []), processedDoc]
      }));
    } finally {
      setProcessing(prev => ({ ...prev, [docType]: false }));
    }
  };

  const getProgress = () => {
    const required = REQUIRED_DOCUMENTS.filter(doc => doc.required);
    const completed = required.filter(doc => uploadedDocs[doc.id]?.length > 0);
    return (completed.length / required.length) * 100;
  };

  return (
    <MobileFormScreen>
      <View style={styles.header}>
        <Text style={styles.title}>Document Collection</Text>
        <Chip icon="progress-check">
          {`${Math.round(getProgress())}% Complete`}
        </Chip>
      </View>

      <ScrollView style={styles.content}>
        {REQUIRED_DOCUMENTS.map((doc) => (
          <Card key={doc.id} style={styles.docCard}>
            <Card.Content>
              <View style={styles.docHeader}>
                <Text style={styles.docTitle}>{doc.title}</Text>
                {doc.required && (
                  <Chip compact mode="outlined" textStyle={styles.requiredChip}>
                    Required
                  </Chip>
                )}
              </View>
              <Text style={styles.docDescription}>{doc.description}</Text>
              
              <DocumentUploader
                onUpload={(file) => handleDocumentUpload(doc.id, file)}
                processing={processing[doc.id]}
                uploadedFiles={uploadedDocs[doc.id] || []}
              />
            </Card.Content>
          </Card>
        ))}
      </ScrollView>

      <View style={styles.footer}>
        <Button
          mode="contained"
          onPress={() => navigation.navigate('PlatformConnection')}
          disabled={getProgress() < 100}
        >
          Continue to Platform Connection
        </Button>
      </View>
    </MobileFormScreen>
  );
};

const styles = StyleSheet.create({
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: SPACING.md
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: COLORS.text.primary
  },
  content: {
    flex: 1,
    padding: SPACING.md
  },
  docCard: {
    marginBottom: SPACING.md
  },
  docHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: SPACING.sm
  },
  docTitle: {
    fontSize: 18,
    fontWeight: '600'
  },
  docDescription: {
    fontSize: 14,
    color: COLORS.text.secondary,
    marginBottom: SPACING.md
  },
  requiredChip: {
    color: COLORS.error
  },
  footer: {
    padding: SPACING.md,
    borderTopWidth: 1,
    borderTopColor: COLORS.divider
  }
});
