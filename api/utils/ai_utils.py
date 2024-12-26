from openai import OpenAI
from .api_config import APIConfig
from .db_utils import get_db_connection
from datetime import datetime
import logging
from typing import Dict, Any, List, Tuple, Optional
import json
import os
from .document_manager import DocumentManager

# Initialize OpenAI client
client = OpenAI(api_key=APIConfig.OPENAI_API_KEY)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# IRS-compliant categories
IRS_CATEGORIES = {
    'advertising': ['marketing', 'ads', 'promotion'],
    'car_expenses': ['vehicle', 'mileage', 'gas', 'maintenance'],
    'insurance': ['liability', 'health', 'business'],
    'office_expense': ['supplies', 'equipment', 'furniture'],
    'travel': ['airfare', 'hotel', 'lodging'],
    'meals': ['restaurant', 'food', 'dining'],
    'utilities': ['phone', 'internet', 'electricity']
}

PATTERN_RECOGNITION = {
    'time_based': {
        'morning': ['breakfast', 'coffee'],
        'afternoon': ['lunch', 'supplies'],
        'evening': ['dinner', 'entertainment']
    },
    'amount_based': {
        'low': {'max': 50, 'typical': ['supplies', 'meals']},
        'medium': {'max': 200, 'typical': ['equipment', 'services']},
        'high': {'min': 200, 'typical': ['travel', 'insurance']}
    }
}

LEARNING_WEIGHTS = {
    'user_corrections': 0.6,
    'pattern_matching': 0.3,
    'historical_data': 0.1
}

def update_learning_system(expense_data: Dict[str, Any], user_correction: str) -> None:
    """Update AI learning system based on user corrections"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Calculate confidence score for the correction
        confidence = calculate_correction_confidence(
            expense_data['description'],
            user_correction,
            expense_data['amount']
        )
    except Exception as e:
        logging.error(f"Error updating learning system: {e}")
        raise

    # Store historical pattern
    store_pattern(
        expense_data['description'],
        user_correction,
        confidence
    )
    
    cursor.execute("""
        INSERT INTO learning_feedback 
        (original_category, corrected_category, description, 
         confidence_score, correction_timestamp)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, (
        expense_data['category'],
        user_correction,
        expense_data['description'],
        confidence
    ))
    conn.commit()

IRS_COMPLIANCE_RULES = {
    'business': {
        'required_fields': ['date', 'amount', 'description'],
        'documentation': ['receipt', 'invoice', 'contract'],
        'categories': ['advertising', 'car_expenses', 'insurance', 'office_expense']
    },
    'personal': {
        'required_fields': ['date', 'amount'],
        'documentation': ['receipt'],
        'categories': ['medical', 'charitable', 'education']
    }
}

PATTERN_WEIGHTS = {
    'frequency': 0.4,
    'amount': 0.3,
    'time_of_day': 0.2,
    'location': 0.1
}

def analyze_pattern_confidence(patterns: Dict[str, Any]) -> float:
    """Calculate confidence score based on patterns"""
    confidence_scores = {
        'frequency': calculate_frequency_confidence(patterns.get('frequency', {})),
        'amount': calculate_amount_confidence(patterns.get('amount', {})),
        'seasonal': calculate_seasonal_confidence(patterns.get('seasonal', {})),
        'vendor': calculate_vendor_confidence(patterns.get('vendor', {})),
        'location': calculate_location_confidence(patterns.get('location', {}))
    }
    
    # Weight and combine confidence scores
    weighted_score = sum(
        score * PATTERN_WEIGHTS.get(pattern_type, 0.1)
        for pattern_type, score in confidence_scores.items()
    )
    
    return weighted_score

def calculate_seasonal_confidence(seasonal_patterns: Dict[str, Any]) -> float:
    """Calculate confidence score for seasonal patterns"""
    if not seasonal_patterns:
        return 0.0
        
    total_matches = sum(
        category_data['count']
        for quarter in seasonal_patterns.values()
        for category_data in quarter.get('categories', {}).values()
    )
    
    return min(total_matches / 20.0, 1.0)  # Normalize to 0-1 range

def calculate_time_confidence(time_patterns: Dict[str, Any]) -> float:
    """Calculate confidence score for time-based patterns"""
    if not time_patterns:
        return 0.0
        
    total_matches = sum(
        category_data['count']
        for time_of_day in time_patterns.values()
        for category_data in time_of_day.get('categories', {}).values()
    )
    
    return min(total_matches / 10.0, 1.0)  # Normalize to 0-1 range

def categorize_expense(description):
    """
    Enhanced AI-based categorization using OpenAI API with learning system integration.
    """
    try:
        # First check learning system for previous categorizations
        learned_categories = get_learned_categories(description)
        if learned_categories:
            best_match = max(learned_categories, key=lambda x: x['confidence'])
            if best_match['confidence'] > 0.8:
                return {
                    'category': best_match['category'],
                    'confidence': best_match['confidence'],
                    'source': 'learning_system'
                }

        # AI-based categorization with enhanced prompting
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "system",
                "content": """Analyze this expense and provide:
                    1. Category (Travel, Meals, Office Supplies, Vehicle, Entertainment, Other)
                    2. Confidence score (0-1)
                    3. Reasoning for categorization
                    4. Tax deductibility assessment
                    Format: category|confidence|reasoning|tax_deductible"""
            }, {
                "role": "user",
                "content": f"Categorize this expense: {description}"
            }]
        )
        result = response.choices[0].message.content.strip().split("|")
        return {
            'category': result[0].strip(),
            'confidence': float(result[1]),
            'reasoning': result[2].strip(),
            'tax_deductible': result[3].strip(),
            'source': 'ai'
        }

def analyze_expense_patterns(expenses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze patterns in expense data for better categorization"""
    patterns = {
        'frequency': analyze_frequency_patterns(expenses),
        'amount': analyze_amount_patterns(expenses),
        'time': analyze_time_patterns(expenses),
        'location': analyze_location_patterns(expenses),
        'vendor': analyze_vendor_patterns(expenses),
        'seasonal': analyze_seasonal_patterns(expenses)
    }
    
    return calculate_pattern_confidence(patterns)

def analyze_location_patterns(expenses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze location-based patterns"""
    location_patterns = {}
    for expense in expenses:
        location = extract_location(expense.get('description', ''))
        if location:
            if location not in location_patterns:
                location_patterns[location] = {
                    'count': 0,
                    'categories': {},
                    'total_amount': 0
                }
            location_patterns[location]['count'] += 1
            location_patterns[location]['total_amount'] += expense.get('amount', 0)
            
            category = expense.get('category')
            if category:
                location_patterns[location]['categories'][category] = \
                    location_patterns[location]['categories'].get(category, 0) + 1
    
    return location_patterns

def analyze_vendor_patterns(expenses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze vendor-specific patterns"""
    vendor_patterns = {}
    for expense in expenses:
        vendor = extract_vendor(expense.get('description', ''))
        if vendor:
            if vendor not in vendor_patterns:
                vendor_patterns[vendor] = {
                    'count': 0,
                    'categories': {},
                    'total_amount': 0
                }
            vendor_patterns[vendor]['count'] += 1
            vendor_patterns[vendor]['total_amount'] += expense.get('amount', 0)
            
            category = expense.get('category')
            if category:
                vendor_patterns[vendor]['categories'][category] = \
                    vendor_patterns[vendor]['categories'].get(category, 0) + 1
    
    return vendor_patterns

def analyze_tax_context(description: str, amount: float) -> Dict[str, Any]:
    """Analyze tax context of an expense with enhanced IRS compliance checking"""
    try:
        # Enhanced tax context analysis
        irs_categories = {
            'business': ['office', 'supplies', 'travel', 'vehicle'],
            'personal': ['groceries', 'entertainment', 'clothing'],
            'mixed': ['phone', 'internet', 'utilities']
        }
        
        description_lower = description.lower()
        context_scores = {
            'business': 0,
            'personal': 0,
            'mixed': 0
        }
        
        # Calculate context scores
        for context, keywords in irs_categories.items():
            score = sum(keyword in description_lower for keyword in keywords)
            context_scores[context] = score / len(keywords)
        
        # Get best matching context
        best_context = max(context_scores.items(), key=lambda x: x[1])
        
        return {
            'context': best_context[0],
            'confidence': best_context[1],
            'suggested_category': get_irs_category(description),
            'deductible_amount': calculate_deductible_amount(amount, best_context[0])
        }
    except Exception as e:
        logging.error(f"Error analyzing tax context: {e}")
        return {
            'context': 'unknown',
            'confidence': 0,
            'suggested_category': 'other',
            'deductible_amount': 0
        }

def get_irs_category(category: str) -> str:
    """Map general category to IRS-compliant category"""
    for irs_cat, keywords in IRS_CATEGORIES.items():
        if any(keyword in category.lower() for keyword in keywords):
            return irs_cat
    return 'other_expenses'

def enhanced_fallback_categorization(description: str) -> Dict[str, Any]:
    """Enhanced AI-based categorization with confidence scoring."""
    categories = {
        'travel': ['flight', 'hotel', 'uber', 'lyft', 'taxi'],
        'meals': ['restaurant', 'food', 'lunch', 'dinner'],
        'office_supplies': ['office', 'supplies', 'paper', 'printer'],
        'utilities': ['phone', 'internet', 'electricity'],
        'vehicle': ['gas', 'maintenance', 'repair', 'parking']
    }
    
    description_lower = description.lower()
    matches = {}
    
    for category, keywords in categories.items():
        score = sum(keyword in description_lower for keyword in keywords)
        if score > 0:
            matches[category] = score / len(keywords)
    
    if matches:
        best_category = max(matches.items(), key=lambda x: x[1])
        return {
            'category': best_category[0],
            'confidence': best_category[1],
            'is_business': True
        }
    
    return {
        'category': 'other',
        'confidence': 0.0,
        'is_business': False
    }

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
        logger.error(f"Error getting tax optimization suggestions: {str(e)}")
        return "Unable to generate tax optimization suggestions at this time."

def analyze_expense_patterns(expenses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze expense patterns for better categorization"""
    patterns = {}
    category_frequencies = {}
    amount_patterns = {}
    time_patterns = {}

    for expense in expenses:
        category = expense.get('category', 'other')
        amount = expense.get('amount', 0)
        date = expense.get('date')
        
        # Update category frequencies
        category_frequencies[category] = category_frequencies.get(category, 0) + 1
        
        # Analyze amount patterns
        amount_range = get_amount_range(amount)
        if amount_range not in amount_patterns:
            amount_patterns[amount_range] = {'categories': {}}
        if category not in amount_patterns[amount_range]['categories']:
            amount_patterns[amount_range]['categories'][category] = 0
        amount_patterns[amount_range]['categories'][category] += 1
        
        # Analyze time patterns
        hour = datetime.strptime(date, '%Y-%m-%d %H:%M:%S').hour
        time_of_day = get_time_of_day(hour)
        if time_of_day not in time_patterns:
            time_patterns[time_of_day] = {'categories': {}}
        if category not in time_patterns[time_of_day]['categories']:
            time_patterns[time_of_day]['categories'][category] = 0
        time_patterns[time_of_day]['categories'][category] += 1

    return patterns

def analyze_frequency_patterns(expenses: List[Dict[str, Any]]) -> Dict[str, float]:
    """Analyze frequency patterns in expenses"""
    frequency_data = {}
    for expense in expenses:
        category = expense.get('category', 'other')
        if category not in frequency_data:
            frequency_data[category] = {
                'count': 0,
                'total': 0,
                'average': 0
            }
        
        frequency_data[category]['count'] += 1
        frequency_data[category]['total'] += expense.get('amount', 0)
    
    # Calculate averages
    for category in frequency_data:
        frequency_data[category]['average'] = (
            frequency_data[category]['total'] / frequency_data[category]['count']
        )
    
    return frequency_data

def analyze_time_patterns(expense_data: Dict[str, Any]) -> Dict[str, float]:
    """Analyze time-based patterns in expenses"""
    try:
        expense_time = datetime.strptime(expense_data['date'], '%Y-%m-%d %H:%M:%S').hour
        time_scores = {}
        
        if 5 <= expense_time < 11:
            period = 'morning'
        elif 11 <= expense_time < 16:
            period = 'afternoon'
        else:
            period = 'evening'
            
        description_lower = expense_data['description'].lower()
        for keyword in PATTERN_RECOGNITION['time_based'][period]:
            if keyword in description_lower:
                time_scores[keyword] = 0.8
                
        return time_scores
    except Exception as e:
        logging.error(f"Error analyzing time patterns: {e}")
        return {}

def analyze_seasonal_patterns(expenses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze seasonal patterns in expenses"""
    seasonal_data = {
        'Q1': {'total': 0, 'count': 0, 'categories': {}},
        'Q2': {'total': 0, 'count': 0, 'categories': {}},
        'Q3': {'total': 0, 'count': 0, 'categories': {}},
        'Q4': {'total': 0, 'count': 0, 'categories': {}},
        'trends': {},
        'year_over_year': {}
    }
    
    for expense in expenses:
        date = datetime.strptime(expense['date'], '%Y-%m-%d')
        quarter = f'Q{(date.month - 1) // 3 + 1}'
        category = expense['category']
        amount = expense['amount']
        
        # Track year-over-year changes
        year = date.year
        if year not in seasonal_data['year_over_year']:
            seasonal_data['year_over_year'][year] = {
                'total': 0,
                'categories': {}
            }
        
        seasonal_data['year_over_year'][year]['total'] += amount
        if category not in seasonal_data['year_over_year'][year]['categories']:
            seasonal_data['year_over_year'][year]['categories'][category] = 0
        seasonal_data['year_over_year'][year]['categories'][category] += amount

    return seasonal_data

def verify_irs_compliance(expense_data: Dict[str, Any]) -> Dict[str, Any]:
    """Verify if expense meets IRS compliance requirements"""
    required_fields = {
        'business': ['date', 'amount', 'description', 'receipt'],
        'personal': ['date', 'amount', 'description']
    }
    
    context = expense_data.get('tax_context', {}).get('context', 'personal')
    fields = required_fields[context]
    
    missing_fields = [
        field for field in fields 
        if not expense_data.get(field)
    ]
    
    compliance_score = (len(fields) - len(missing_fields)) / len(fields)
    
    return {
        'is_compliant': len(missing_fields) == 0,
        'compliance_score': compliance_score,
        'missing_fields': missing_fields,
        'context': context
    }

def analyze_historical_patterns(description: str) -> Dict[str, float]:
    """Analyze historical patterns for better categorization"""

def analyze_amount_patterns(expenses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze amount-based patterns in expenses"""
    amount_patterns = {
        'low': {'max': 50, 'categories': {}},
        'medium': {'max': 200, 'categories': {}},
        'high': {'min': 200, 'categories': {}}
    }
    
    for expense in expenses:
        amount = expense.get('amount', 0)
        category = expense.get('category', 'other')
        
        if amount <= 50:
            range_key = 'low'
        elif amount <= 200:
            range_key = 'medium'
        else:
            range_key = 'high'
            
        if category not in amount_patterns[range_key]['categories']:
            amount_patterns[range_key]['categories'][category] = 0
        amount_patterns[range_key]['categories'][category] += 1
    
    return amount_patterns

def calculate_pattern_confidence(patterns: Dict[str, Any]) -> float:
    """Calculate overall confidence score from patterns"""
    if not patterns:
        return 0.0
    
    confidence_scores = {
        'frequency': calculate_frequency_confidence(patterns.get('frequency', {})),
        'amount': calculate_amount_confidence(patterns.get('amount', {})),
        'time': calculate_time_confidence(patterns.get('time', {})),
        'location': calculate_location_confidence(patterns.get('location', {}))
    }
    
    return sum(confidence_scores.values()) / len(confidence_scores)

def get_amount_range(amount: float) -> str:
    """Get the range category for an amount"""
    if amount <= 50:
        return 'low'
    elif amount <= 200:
        return 'medium'
    return 'high'

def get_time_of_day(hour: int) -> str:
    """Get the time of day category"""
    if 5 <= hour < 12:
        return 'morning'
    elif 12 <= hour < 17:
        return 'afternoon'
    elif 17 <= hour < 22:
        return 'evening'
    return 'night'

def calculate_deductible_amount(amount: float, context: str) -> float:
    """Calculate deductible amount based on context"""
    deduction_rates = {
        'business': 1.0,
        'personal': 0.0,
        'mixed': 0.5
    }
    
    rate = deduction_rates.get(context, 0.0)
    return amount * rate

def calculate_correction_confidence(description: str, category: str, amount: float) -> float:
    """Calculate confidence score for user corrections"""
    confidence = 0.0
    
    # Check if category matches known patterns
    if any(keyword in description.lower() for keyword in IRS_CATEGORIES.get(category, [])):
        confidence += 0.4
    
    # Check amount ranges
    if amount < 50 and category in ['meals', 'supplies']:
        confidence += 0.3
    elif 50 <= amount <= 200 and category in ['equipment', 'services']:
        confidence += 0.3
    elif amount > 200 and category in ['travel', 'insurance']:
        confidence += 0.3
    
    return min(confidence + 0.3, 1.0)  # Base confidence of 0.3

def calculate_frequency_confidence(frequency_data: Dict[str, Any]) -> float:
    """Calculate confidence based on frequency patterns"""
    if not frequency_data:
        return 0.0
    
    total_occurrences = sum(data['count'] for data in frequency_data.values())
    if total_occurrences == 0:
        return 0.0
    
    max_frequency = max(data['count'] for data in frequency_data.values())
    return min(max_frequency / total_occurrences, 1.0)

def calculate_amount_confidence(amount_data: Dict[str, Any]) -> float:
    """Calculate confidence based on amount patterns"""
    if not amount_data:
        return 0.0
    
    consistency_score = len(amount_data.get('categories', {})) / 10.0
    return min(consistency_score, 1.0)

def calculate_vendor_confidence(vendor_data: Dict[str, Any]) -> float:
    """Calculate confidence based on vendor patterns"""
    if not vendor_data:
        return 0.0
    
    vendor_consistency = vendor_data.get('count', 0) / 10.0
    return min(vendor_consistency, 1.0)

def calculate_location_confidence(location_data: Dict[str, Any]) -> float:
    """Calculate confidence based on location patterns"""
    if not location_data:
        return 0.0
    
    location_frequency = location_data.get('count', 0) / 5.0
    return min(location_frequency, 1.0)

def store_pattern(description: str, category: str, confidence: float) -> None:
    """Store pattern in the database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO patterns (description, category, confidence, timestamp)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        """, (description, category, confidence))
        
        conn.commit()
    except Exception as e:
        logging.error(f"Error storing pattern: {e}")

def extract_location(description: str) -> Optional[str]:
    """Extract location information from description"""
    common_locations = ['office', 'store', 'restaurant', 'hotel']
    description_lower = description.lower()
    
    for location in common_locations:
        if location in description_lower:
            return location
    return None

def extract_vendor(description: str) -> Optional[str]:
    """Extract vendor information from description"""
    # Remove common words and punctuation
    common_words = ['the', 'at', 'from', 'by', 'in', 'on', 'for']
    words = description.lower().split()
    
    # Remove common words and get first remaining word as vendor
    filtered_words = [word for word in words if word not in common_words]
    return filtered_words[0] if filtered_words else None

class LearningSystem:
    def __init__(self):
        self.conn = get_db_connection()
        self.min_confidence_threshold = 0.7
        
    def learn_from_correction(self, 
                            original_category: str, 
                            corrected_category: str, 
                            description: str) -> None:
        """Learn from user corrections"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO category_learning 
                (original_category, corrected_category, description, timestamp)
                VALUES (?, ?, ?, ?)
            """, (
                original_category,
                corrected_category,
                description,
                datetime.now().isoformat()
            ))
            self.conn.commit()
        except Exception as e:
            logging.error(f"Error learning from correction: {e}")

def get_learned_categories(description: str) -> List[Dict[str, float]]:
    """Get categories based on learning history"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT corrected_category, COUNT(*) as count
            FROM category_learning
            WHERE description LIKE ?
            GROUP BY corrected_category
            ORDER BY count DESC
            LIMIT 5
        """, (f"%{description}%",))
        
        results = cursor.fetchall()
        total = sum(row['count'] for row in results)
        
        return [{
            'category': row['corrected_category'],
            'confidence': row['count'] / total
        } for row in results]
    except Exception as e:
        logging.error(f"Error getting learned categories: {e}")
        return []
