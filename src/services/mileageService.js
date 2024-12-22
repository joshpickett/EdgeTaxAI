const BASE_URL = "https://your-backend-api.com/api";

// Call backend to calculate mileage
export const calculateMileage = async (tripData) => {
  try {
    const response = await fetch(`${BASE_URL}/mileage`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(tripData),
    });
    const data = await response.json();

    if (response.ok) {
      // Create expense entry automatically
      await fetch(`${BASE_URL}/expenses`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          type: "mileage",
          ...data
        }),
      });
      return data;
    } else {
      throw new Error(data.error || "Failed to calculate mileage.");
    }
  } catch (error) {
    console.error("Error calculating mileage:", error.message);
    throw error;
  }
};
