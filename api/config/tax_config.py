from decimal import Decimal

TAX_CONFIG = {
    # Tax brackets for 2023 (example)
    'TAX_BRACKETS': [
        (0, 11000, Decimal('0.10')),
        (11001, 44725, Decimal('0.12')),
        (44726, 95375, Decimal('0.22')),
        (95376, 182100, Decimal('0.24')),
        (182101, 231250, Decimal('0.32')),
        (231251, 578125, Decimal('0.35')),
        (578126, float('inf'), Decimal('0.37'))
    ],
    
    # Self-employment tax rate
    'SELF_EMPLOYMENT_TAX_RATE': Decimal('0.153'),
    
    # Standard deduction amounts
    'STANDARD_DEDUCTION': {
        'single': 13850,
        'married': 27700,
        'head_of_household': 20800
    },
    
    # Quarterly tax payment deadlines
    'QUARTERLY_DEADLINES': {
        1: '04-15',
        2: '06-15',
        3: '09-15',
        4: '01-15'
    },
    
    # Cache settings
    'CACHE_SETTINGS': {
        'tax_calculation': 3600,  # 1 hour
        'quarterly_estimate': 86400,  # 24 hours
        'deduction_analysis': 1800  # 30 minutes
    },
    
    # Rate limiting settings
    'RATE_LIMITS': {
        'tax_calculation': 60,  # requests per minute
        'document_generation': 30,  # requests per minute
        'deduction_analysis': 45  # requests per minute
    }
}
