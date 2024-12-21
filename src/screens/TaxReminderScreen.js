import React, { useState } from "react";
import { View, Text, TextInput, Button, StyleSheet, Alert } from "react-native";

const TaxReminderScreen = ({ userId }) => {
  const [phoneNumber, setPhoneNumber] = useState("");
  const [reminderDate, setReminderDate] = useState("");

  const handleSetReminder = async () => {
    if (!phoneNumber || !reminderDate) {
      Alert.alert("Error", "Both phone number and reminder date are required.");
      return;
    }

    try {
      const response = await fetch("https://your-backend-api.com/api/tax/reminders", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: userId,
          phone_number: phoneNumber,
          reminder_date: reminderDate,
        }),
      });

      const data = await response.json();
      if (response.ok) {
        Alert.alert("Success", "Tax reminder scheduled successfully!");
      } else {
        throw new Error(data.error || "Failed to schedule reminder.");
      }
    } catch (error) {
      console.error("Error scheduling tax reminder:", error.message);
      Alert.alert("Error", "Failed to schedule tax reminder.");
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Set Tax Reminder</Text>
      <TextInput
        style={styles.input}
        placeholder="Enter Phone Number (+1234567890)"
        keyboardType="phone-pad"
        value={phoneNumber}
        onChangeText={setPhoneNumber}
      />
      <TextInput
        style={styles.input}
        placeholder="Reminder Date (YYYY-MM-DD)"
        value={reminderDate}
        onChangeText={setReminderDate}
      />
      <Button title="Schedule Reminder" onPress={handleSetReminder} color="#007BFF" />
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, backgroundColor: "#f9f9f9" },
  title: { fontSize: 22, fontWeight: "bold", textAlign: "center", marginBottom: 20 },
  input: {
    borderWidth: 1,
    borderColor: "#ccc",
    padding: 10,
    marginBottom: 10,
    borderRadius: 5,
    backgroundColor: "#fff",
  },
});

export default TaxReminderScreen;
