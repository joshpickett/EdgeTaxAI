import React, { useState } from 'react';
import { View, Image, StyleSheet } from 'react-native';
import { Button, Text, ActivityIndicator } from 'react-native-paper';
import * as DocumentPicker from 'expo-document-picker';
import * as FileSystem from 'expo-file-system';
import { COLORS } from '../../assets/config/colors';
import { SPACING } from '../../assets/config/spacing';

interface DocumentUploaderProps {
  onUpload: (file: any) => Promise<void>;
  processing: boolean;
  uploadedFiles: any[];
}

export const DocumentUploader: React.FC<DocumentUploaderProps> = ({
  onUpload,
  processing,
  uploadedFiles
}) => {
  const [error, setError] = useState<string | null>(null);

  const handleFilePick = async () => {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: ['image/*', 'application/pdf'],
        copyToCacheDirectory: true
      });

      if (result.type === 'success') {
        const fileInfo = await FileSystem.getInfoAsync(result.uri);
        
        // Validate file size (max 10MB)
        if (fileInfo.size && fileInfo.size > 10 * 1024 * 1024) {
          setError('File size must be less than 10MB');
          return;
        }

        setError(null);
        await onUpload(result);
      }
    } catch (err) {
      setError('Error uploading document. Please try again.');
      console.error('Document upload error:', err);
    }
  };

  return (
    <View style={styles.container}>
      {uploadedFiles.length > 0 && (
        <View style={styles.previewContainer}>
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
      )}

      <Button
        mode="outlined"
        onPress={handleFilePick}
        loading={processing}
        disabled={processing}
        icon="upload"
      >
        Upload Document
      </Button>

      {error && (
        <Text style={styles.error}>{error}</Text>
      )}

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
  }
});
