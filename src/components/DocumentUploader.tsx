import React, { useState } from 'react';
import { View, StyleSheet } from 'react-native';
import { Button, Text, ActivityIndicator, ProgressBar } from 'react-native-paper';
import * as DocumentPicker from 'expo-document-picker';
import * as FileSystem from 'expo-file-system';
import { COLORS } from '../../assets/config/colors';
import { SPACING } from '../../assets/config/spacing';
import { DocumentValidationService } from '../services/documentValidationService';
import { ErrorMessage } from './ErrorMessage';

interface DocumentUploaderProps {
  onUpload: (file: any) => Promise<void>;
  processing: boolean;
  uploadedFiles: any[];
  acceptedTypes?: string[];
  maxSize?: number;
  validateContent?: boolean;
}

const defaultAcceptedTypes = ['application/pdf', 'image/jpeg', 'image/png'];
const defaultMaxSize = 10 * 1024 * 1024; // 10MB

export const DocumentUploader: React.FC<DocumentUploaderProps> = ({
  onUpload,
  processing,
  uploadedFiles,
  acceptedTypes = defaultAcceptedTypes,
  maxSize = defaultMaxSize,
  validateContent = true
}) => {
  const [error, setError] = useState<string | null>(null);
  const [validationProgress, setValidationProgress] = useState<number>(0);
  const documentValidationService = new DocumentValidationService();

  const handleFilePick = async () => {
    try {
      setError(null);
      const file = await DocumentPicker.getDocumentAsync({
        type: acceptedTypes,
        copyToCacheDirectory: true,
      });
      
      if (!validateFile(file)) {
        return;
      }
      
      if (validateContent) {
        await validateDocumentContent(file);
      }

      await onUpload(file);
    } catch (err) {
      handleError(err);
    }
  };

  const validateFile = (file: any): boolean => {
    if (!file) {
      setError('No file selected');
      return false;
    }

    if (!acceptedTypes.includes(file.type)) {
      setError(`Invalid file type. Accepted types: ${acceptedTypes.join(', ')}`);
      return false;
    }

    if (file.size > maxSize) {
      setError(`File size must be less than ${maxSize / (1024 * 1024)}MB`);
      return false;
    }

    return true;
  };

  const validateDocumentContent = async (file: any) => {
    try {
      setValidationProgress(0);
      const result = await documentValidationService.validateDocument(file, (progress) => {
        setValidationProgress(progress);
      });

      if (!result.isValid) {
        setError(result.error);
        return false;
      }
      return true;
    } catch (err) {
      handleError(err);
      return false;
    }
  };

  const handleError = (err: any) => {
    setError('Error uploading document. Please try again.');
    console.error('Document upload error:', err);
  };

  return (
    <View style={styles.container}>
      <View style={styles.previewContainer}>
        {error && (
          <ErrorMessage message={error} type="error" />
        )}
        
        {validationProgress > 0 && validationProgress < 100 && (
          <View style={styles.progressContainer}>
            <Text>Validating document: {validationProgress}%</Text>
            <ProgressBar progress={validationProgress / 100} />
          </View>
        )}
        
        {uploadedFiles.map((file, index) => (
          <View key={index} style={styles.preview}>
            {file.type === 'image' ? (
              <Image
                source={{ uri: file.uri }}
                style={styles.previewImage}
              />
            ) : (
              <View style={styles.pdfPreview}>
                <Text>PDF Document</Text>
              </View>
            )}
          </View>
        ))}
      </View>

      <Button
        mode="outlined"
        onPress={handleFilePick}
        loading={processing}
        disabled={processing}
        icon="upload"
      >
        Upload Document
      </Button>

      {processing && (
        <View style={styles.processingContainer}>
          <ActivityIndicator size="small" />
          <Text style={styles.processingText}>
            Processing document...
          </Text>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginTop: SPACING.md
  },
  previewContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: SPACING.md
  },
  preview: {
    width: 100,
    height: 100,
    marginRight: SPACING.sm,
    marginBottom: SPACING.sm,
    borderRadius: 8,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: COLORS.border
  },
  previewImage: {
    width: '100%',
    height: '100%'
  },
  pdfPreview: {
    width: '100%',
    height: '100%',
    backgroundColor: COLORS.surface,
    justifyContent: 'center',
    alignItems: 'center'
  },
  error: {
    color: COLORS.error,
    marginTop: SPACING.sm
  },
  processingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: SPACING.sm
  },
  processingText: {
    marginLeft: SPACING.sm,
    color: COLORS.text.secondary
  },
  progressContainer: {
    marginBottom: SPACING.md
  }
});
