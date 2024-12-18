def categorize_expense(description):
    """
    Simple AI-based categorization logic for expenses.
    """
    if "lunch" in description.lower() or "food" in description.lower():
        return "Meals & Entertainment"
    elif "travel" in description.lower():
        return "Travel"
    elif "office" in description.lower() or "supplies" in description.lower():
        return "Office Supplies"
    elif "business" in description.lower():
        return "Business Expense"
    return "Other"
