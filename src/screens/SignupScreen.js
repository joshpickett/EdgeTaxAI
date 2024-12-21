import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, Alert, ScrollView } from 'react-native';
import { useDispatch, useSelector } from 'react-redux';
import CustomButton from '../components/CustomButton';
import LoadingState from '../components/LoadingState';
import ErrorMessage from '../components/ErrorMessage';
import InputField from '../components/InputField';
import { signupUser, verifyOTP, clearErrors } from '../store/slices/authSlice';

const SignupScreen = ({ navigation }) => {
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [otp, setOtp] = useState('');
  const [formErrors, setFormErrors] = useState({});

  const dispatch = useDispatch();
  const { loading, error, otpSent } = useSelector(state => state.auth);

  useEffect(() => {
    return () => {
      dispatch(clearErrors());
    };
  }, [dispatch]);

  const handleSignup = async () => {
    try {
      // Enhanced validation
      const errors = {};
      if (!email && !phone) {
        errors.identifier = 'Please enter either email or phone number';
      }
      if (email && !validateEmail(email)) {
        errors.email = 'Invalid email format';
      }
      if (phone && !validatePhone(phone)) {
        errors.phone = 'Invalid phone format';
      }

      if (Object.keys(errors).length > 0) {
        setFormErrors(errors);
        return;
      }

      setFormErrors({});
      const identifier = email || phone;
      const result = await dispatch(signupUser({ identifier })).unwrap();
      
      if (result.success) {
        Alert.alert('Success', 'OTP sent successfully!');
      }
    } catch (error) {
      Alert.alert('Error', error.message || 'Failed to send OTP');
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>Create Account</Text>

      {loading && <LoadingState />}
      {error && <ErrorMessage message={error} />}

      <InputField
        label="Email"
        placeholder="Enter your email"
        value={email}
        onChangeText={setEmail}
        error={formErrors.email}
        keyboardType="email-address"
        autoCapitalize="none"
      />

      <InputField
        label="Phone"
        placeholder="Enter your phone"
        value={phone}
        onChangeText={setPhone}
        error={formErrors.phone}
        keyboardType="phone-pad"
      />

      {otpSent ? (
        <View style={styles.otpContainer}>
          <Text style={styles.otpText}>Enter the OTP sent to {email || phone}</Text>
          <InputField
            label="OTP"
            placeholder="Enter OTP"
            value={otp}
            onChangeText={setOtp}
          />
        </View>
      ) : (
        <CustomButton title="Sign Up" onPress={handleSignup} />
      )}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
  },
  title: {
    fontSize: 24,
    marginBottom: 20,
    textAlign: 'center',
  },
  otpContainer: {
    marginTop: 20,
    alignItems: 'center',
  },
  otpText: {
    fontSize: 16,
    marginBottom: 10,
  },
});

const validateEmail = (email) => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(String(email).toLowerCase());
};

const validatePhone = (phone) => {
  const re = /^[0-9]{10}$/;
  return re.test(String(phone));
};

export default SignupScreen;
