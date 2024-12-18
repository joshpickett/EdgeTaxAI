const BASE_URL = "https://your-backend-api.com/api";

// Call backend to calculate mileage
export const calculateMileage = async (start, end) => {
  try {
    const response = await fetch(`${BASE_URL}/mileage`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ start, end }),
    });
    const data = await response.json();

    if (response.ok) {
      return data.distance; // Example: "12.3 km"
    } else {
      throw new Error(data.error || "Failed to calculate mileage.");
    }
  } catch (error) {
    console.error("Error calculating mileage:", error.message);
    throw error;
  }
};
