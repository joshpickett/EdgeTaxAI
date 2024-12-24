export const formatMileage = (distance: number): string => {
  return `${distance.toFixed(1)} miles`;
};

export const formatTaxDeduction = (amount: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'United States Dollar'
  }).format(amount);
};

export const formatDate = (date: string): string => {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
};

export const formatPurpose = (purpose: string): string => {
  return purpose.charAt(0).toUpperCase() + purpose.slice(1).toLowerCase();
};
