// Email validation regex
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

// Phone number validation regex (basic international format)
const PHONE_REGEX = /^\+?[1-9]\d{1,14}$/;

export const validateEmail = (email) => {
  if (!email) return "Email is required";
  if (!EMAIL_REGEX.test(email)) return "Invalid email format";
  return null;
};

export const validatePhone = (phone) => {
  if (!phone) return "Phone number is required";
  if (!PHONE_REGEX.test(phone)) return "Invalid phone number format";
  return null;
};

export const validatePassword = (password) => {
  if (!password) return "Password is required";
  if (password.length < 8) return "Password must be at least 8 characters";
  return null;
};

export const validateAmount = (amount) => {
  if (!amount) return "Amount is required";
  if (isNaN(amount) || parseFloat(amount) <= 0) {
    return "Amount must be a positive number";
  }
  return null;
};

export const validateDescription = (description) => {
  if (!description) return "Description is required";
  if (description.length < 3) return "Description must be at least 3 characters";
  return null;
};

export const validateDate = (date) => {
  if (!date) return "Date is required";
  if (isNaN(Date.parse(date))) return "Invalid date format";
  return null;
};
