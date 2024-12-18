const BASE_URL = "https://your-backend-api.com/api"; // Update with your backend base URL

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
    return data.savings; // Returns calculated tax savings
  } catch (error) {
    console.error("Error fetching tax savings:", error);
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
    return data.suggestions; // Returns list of AI-suggested deductions
  } catch (error) {
    console.error("Error fetching deduction suggestions:", error);
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
    return data.tax_rate; // Returns the tax rate
  } catch (error) {
    console.error("Error fetching tax rate:", error);
    throw error;
  }
};

