import json
import os

# Load categories from the categories.json file
CATEGORIES_FILE = os.path.join(os.path.dirname(__file__), "utils", "categories.json")


def load_categories():
    """Load and return categories from the JSON file."""
    try:
        with open(CATEGORIES_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"Categories file not found at {CATEGORIES_FILE}")
    except json.JSONDecodeError:
        raise ValueError(f"Error decoding categories JSON file at {CATEGORIES_FILE}")


def categorize_expense(description):
    """
    Categorize the expense based on keywords in the description.
    Defaults to 'General' if no match is found.
    """
    categories = load_categories()
    description_lower = description.lower() if description else ""

    for category, keywords in categories.items():
        if any(keyword.lower() in description_lower for keyword in keywords):
            return category

    return "General"  # Default category if no match is found
