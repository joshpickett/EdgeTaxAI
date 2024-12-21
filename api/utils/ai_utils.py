from openai import OpenAI
from .api_config import APIConfig
import logging
import json

# Initialize OpenAI client
client = OpenAI(api_key=APIConfig.OPENAI_API_KEY)

def categorize_expense(description):
    """
    Enhanced AI-based categorization using OpenAI API.
    Falls back to rule-based categorization if API fails.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "system",
                "content": "Categorize this expense into one of these categories: Travel, Meals, Office Supplies, Vehicle, Entertainment, Other"
            }, {
                "role": "user",
                "content": f"Categorize this expense: {description}"
            }]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"OpenAI API error: {str(e)}")
        return fallback_categorization(description)

def fallback_categorization(description):
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

def get_tax_optimization_suggestions(expenses):
    """
    Get AI-powered tax optimization suggestions based on expense data.
    """
    try:
        # Format expenses for AI prompt
        expense_summary = json.dumps([{
            "description": exp["description"],
            "amount": exp["amount"],
            "category": exp["category"]
        } for exp in expenses])

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "system",
                "content": "You are a tax optimization expert. Analyze these expenses and suggest tax deductions."
            }, {
                "role": "user",
                "content": f"Analyze these expenses and suggest potential tax deductions: {expense_summary}"
            }]
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"Error getting tax optimization suggestions: {str(e)}")
        return "Unable to generate tax optimization suggestions at this time."
