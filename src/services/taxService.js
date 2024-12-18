const BASE_URL = "https://your-backend-api.com/api"; // Replace with your backend base URL

// Fetch Real-Time Tax Savings
export const getTaxSavings = async (amount) => {
  try {
    const response = await fetch(`${BASE_URL}/tax/savings`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ amount }),
    });

    if (!response.ok) {
      throw new Error("Failed to fetch tax savings.");
    }

    const data = await response.json();
    return data.savings; // Returns the calculated tax savings amount
  } catch (error) {
    console.error("Error fetching tax savings:", error.message);
    throw error;
  }
};

// Fetch AI Deduction Suggestions
export const getDeductionSuggestions = async (expenses) => {
  try {
    const response = await fetch(`${BASE_URL}/tax/deductions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ expenses }),
    });

    if (!response.ok) {
      throw new Error("Failed to fetch deduction suggestions.");
    }

    const data = await response.json();
    return data.suggestions; // Returns the AI-suggested deduction list
  } catch (error) {
    console.error("Error fetching deduction suggestions:", error.message);
    throw error;
  }
};

// Fetch Centralized Tax Rate
export const getTaxRate = async () => {
  try {
    const response = await fetch(`${BASE_URL}/config`); // Fetch tax rate from /api/config
    if (!response.ok) {
      throw new Error("Failed to fetch tax rate.");
    }

    const data = await response.json();
    return data.tax_rate; // Returns the centralized tax rate
  } catch (error) {
    console.error("Error fetching tax rate:", error.message);
    throw error;
  }
};

// Fetch Detailed Tax Reports
export const getTaxReports = async (userId) => {
  try {
    const response = await fetch(`${BASE_URL}/reports/${userId}`, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    });

    if (!response.ok) {
      throw new Error("Failed to fetch tax reports.");
    }

    const data = await response.json();
    return data.reports; // Returns detailed tax reports
  } catch (error) {
    console.error("Error fetching tax reports:", error.message);
    throw error;
  }
};
