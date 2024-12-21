import React, { useEffect, useState } from "react";
import { View, Text, TextInput, Button, StyleSheet, Alert, ActivityIndicator, Linking } from "react-native";
import { getProfile, updateProfile } from "../services/authService"; // Updated imports

const ProfileScreen = () => {
  const [profile, setProfile] = useState({ full_name: "", email: "", phone_number: "" });
  const [loading, setLoading] = useState(true);

  // Fetch Profile Details
  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const data = await getProfile();
        setProfile(data);
      } catch (error) {
        Alert.alert("Error", "Failed to fetch profile details.");
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, []);

  // Handle Profile Update
  const handleUpdate = async () => {
    try {
      await updateProfile(profile.full_name, profile.email, profile.phone_number);
      Alert.alert("Success", "Profile updated successfully!");
    } catch (error) {
      Alert.alert("Error", "Failed to update profile.");
    }
  };

  // Handle Connect Platform
  const handleConnectPlatform = (platform) => {
    const url = `https://your-backend-api.com/api/gig/connect/${platform}`;
    Linking.openURL(url).catch(() => Alert.alert("Error", `Failed to connect ${platform}.`));
  };

  if (loading) {
    return <ActivityIndicator size="large" color="#007BFF" />;
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Profile</Text>

      {/* Profile Update Section */}
      <TextInput
        style={styles.input}
        placeholder="Full Name"
        value={profile.full_name}
        onChangeText={(text) => setProfile({ ...profile, full_name: text })}
      />
      <TextInput
        style={styles.input}
        placeholder="Email"
        value={profile.email}
        onChangeText={(text) => setProfile({ ...profile, email: text })}
        keyboardType="email-address"
      />
      <TextInput
        style={styles.input}
        placeholder="Phone Number"
        value={profile.phone_number}
        onChangeText={(text) => setProfile({ ...profile, phone_number: text })}
        keyboardType="phone-pad"
      />
      <Button title="Update Profile" onPress={handleUpdate} color="#28A745" />

      {/* Gig Platform Integration */}
      <Text style={styles.subTitle}>Connect Gig Platforms</Text>
      <Button title="Connect Uber" onPress={() => handleConnectPlatform("uber")} color="#007BFF" />
      <Button title="Connect Lyft" onPress={() => handleConnectPlatform("lyft")} color="#FF69B4" />
      <Button title="Connect DoorDash" onPress={() => handleConnectPlatform("doordash")} color="#FF4500" />
      <Button title="Connect Instacart" onPress={() => handleConnectPlatform("instacart")} color="#32CD32" />
      <Button title="Connect Upwork" onPress={() => handleConnectPlatform("upwork")} color="#008080" />
      <Button title="Connect Fiverr" onPress={() => handleConnectPlatform("fiverr")} color="#FFBF00" />
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, backgroundColor: "#F9F9F9" },
  title: { fontSize: 22, fontWeight: "bold", marginBottom: 20, textAlign: "center" },
  subTitle: { fontSize: 18, fontWeight: "bold", marginTop: 30, marginBottom: 10 },
  input: {
    borderWidth: 1,
    borderColor: "#CCC",
    padding: 10,
    marginBottom: 15,
    borderRadius: 5,
    backgroundColor: "#FFF",
  },
});

export default ProfileScreen;
