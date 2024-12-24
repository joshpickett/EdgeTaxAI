import sharedTaxService from '../../../shared/services/taxService';

export const getTaxSavings = async (amount) => {
  try {
    return await sharedTaxService.calculateTaxSavings(amount);
  } catch (error) {
    console.error("Error fetching tax savings:", error.message);
    throw error;
  }
};

export const analyzeDeductions = async (expenses) => {
  try {
    return await sharedTaxService.analyzeTaxDeductions(expenses);
  } catch (error) {
    console.error("Error fetching deduction suggestions:", error.message);
    throw error;
  }
};

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
