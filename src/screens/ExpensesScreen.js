import React, { useState, useEffect } from "react";
import { View, Text, TextInput, StyleSheet, Alert, Image } from "react-native";
import CustomButton from "../components/CustomButton";
import LoadingState from "../components/LoadingState";
import ErrorMessage from "../components/ErrorMessage";
import { expenseService } from "../services/expenseService";
import { processReceipt } from "../services/ocrService";
import * as ImagePicker from 'expo-image-picker';
import { colors, typography, spacing } from '../styles/tokens';

// Asset paths
const ASSETS_DIR = '../assets';
const EXPENSE_ICON = `${ASSETS_DIR}/logo/icon/edgetaxai-icon-color.svg`;

const ExpensesScreen = ({ navigation }) => {
  const [description, setDescription] = useState("");
  const [amount, setAmount] = useState("");
  const [category, setCategory] = useState("");
  const [receiptImage, setReceiptImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  useEffect(() => {
    requestCameraPermission();
  }, []);

  const requestCameraPermission = async () => {
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permission needed', 'Camera permission is required to upload receipts');
    }
  };

  const handleAddExpense = async () => {
    // Clear previous errors
    setErrors({});

    // Validate all fields
    const descError = validateDescription(description);
    const amountError = validateAmount(amount);
    
    if (descError || amountError) {
      setErrors({
        description: descError,
        amount: amountError,
      });
      return;
    }

    // Proceed with adding the expense
    // ...rest of the code...
  };

  const handleReceiptUpload = async () => {
    try {
      const result = await ImagePicker.launchCameraAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        quality: 1,
      });

      if (!result.canceled) {
        setLoading(true);
        const receiptData = await processReceipt(result.uri);
        if (receiptData) {
          setDescription(receiptData.description || '');
          setAmount(receiptData.amount?.toString() || '');
          setCategory(receiptData.category || '');
        }
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to process receipt');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Image source={EXPENSE_ICON} style={styles.icon} />
      <Text style={styles.title}>Add Expense</Text>
      <TextInput
        style={[styles.input, errors.description && styles.inputError]}
        placeholder="Description"
        value={description}
        onChangeText={setDescription}
      />
      {errors.description && <Text style={styles.errorText}>{errors.description}</Text>}
      <TextInput
        style={[styles.input, errors.amount && styles.inputError]}
        placeholder="Amount"
        value={amount}
        onChangeText={setAmount}
        keyboardType="numeric"
      />
      {errors.amount && <Text style={styles.errorText}>{errors.amount}</Text>}
      <CustomButton title="Add Expense" onPress={handleAddExpense} />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: spacing.lg,
    backgroundColor: colors.background.default,
  },
  title: {
    fontSize: typography.fontSize.xl,
    fontWeight: typography.fontWeight.bold,
    color: colors.text.primary,
    marginBottom: 20,
  },
  input: {
    borderWidth: 1,
    borderColor: '#ccc',
    padding: 10,
    borderRadius: 5,
    marginBottom: 10,
  },
  inputError: {
    borderColor: '#ff0000',
  },
  errorText: {
    color: '#ff0000',
    fontSize: 12,
    marginTop: 5,
  },
  icon: {
    width: 50,
    height: 50,
    marginBottom: spacing.md,
  },
});
