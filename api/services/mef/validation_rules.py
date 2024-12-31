from typing import Dict, Any, List
from decimal import Decimal
from datetime import datetime
from api.services.error_handling_service import ErrorHandlingService

class BusinessRules:
    """Business rules for tax forms"""
    # Existing thresholds
    NEC_THRESHOLD = Decimal('600.00')
    K_THRESHOLD = Decimal('20000.00')
    EZ_INCOME_THRESHOLD = Decimal('100000.00')
    
    # International thresholds
    FBAR_THRESHOLD = Decimal('10000.00')
    FOREIGN_EARNED_INCOME_EXCLUSION = Decimal('120000.00')
    FOREIGN_HOUSING_EXCLUSION = Decimal('15000.00')
    
    # Currency validation thresholds
    MAX_CURRENCY_RATE_AGE = 1  # Max age of exchange rate in days
    
    # Treaty benefit thresholds
    MIN_FOREIGN_TAX_RATE = Decimal('0.10')  # 10% minimum foreign tax rate
    MAX_TREATY_BENEFIT = Decimal('1000000.00')

def validate_tin_format(tin: str) -> bool:
    """Validate TIN format (SSN or EIN)"""
    if not tin or len(tin.replace('-', '').replace(' ', '')) != 9:
        return False
    clean_tin = tin.replace('-', '').replace(' ', '')
    if not clean_tin.isdigit():
        return False
    return True
        
@staticmethod
def validate_foreign_address(address: Dict[str, Any]) -> List[str]:
    """Validate foreign address format"""
    errors = []
    required_fields = ['street', 'city', 'country']
    
    for field in required_fields:
        if not address.get(field):
            errors.append(f"{field} is required for foreign address")
            
    # Validate country code format
    if address.get('country') and len(address['country']) != 2:
        errors.append("Country must be a valid 2-letter ISO code")
        
    # Validate postal code format if present
    if address.get('postal_code') and not BusinessRules._validate_postal_code(
        address['postal_code'], 
        address.get('country')
    ):
        errors.append("Invalid postal code format for country")
        
    return errors
        
@staticmethod
def validate_currency(amount: Decimal, currency_code: str, exchange_rate: Dict[str, Any]) -> List[str]:
    """Validate currency and exchange rate"""
    errors = []
    
    if not currency_code or len(currency_code) != 3:
        errors.append("Invalid currency code")
        
    if not exchange_rate.get('rate'):
        errors.append("Exchange rate is required")
    
    # Validate exchange rate age
    if exchange_rate.get('date'):
        rate_date = datetime.fromisoformat(exchange_rate['date'])
        age_days = (datetime.now() - rate_date).days
        if age_days > BusinessRules.MAX_CURRENCY_RATE_AGE:
            errors.append("Exchange rate is too old")
            
    return errors
        
@staticmethod
def validate_treaty_benefits(data: Dict[str, Any]) -> List[str]:
    """Validate treaty benefit claims"""
    errors = []
    
    if not data.get('treaty_country'):
        errors.append("Treaty country is required")
        
    if not data.get('article_number'):
        errors.append("Treaty article number is required")
        
    benefit_amount = Decimal(str(data.get('benefit_amount', 0)))
    if benefit_amount > BusinessRules.MAX_TREATY_BENEFIT:
        errors.append("Treaty benefit amount exceeds maximum allowed")
        
    # Validate foreign tax rate
    foreign_tax_rate = Decimal(str(data.get('foreign_tax_rate', 0)))
    if foreign_tax_rate < BusinessRules.MIN_FOREIGN_TAX_RATE:
        errors.append("Foreign tax rate below minimum required for treaty benefits")
        
    return errors
        
@staticmethod
def validate_foreign_tax_credit(data: Dict[str, Any]) -> List[str]:
    """Validate foreign tax credit claims"""
    errors = []
    
    if not data.get('foreign_tax_paid'):
        errors.append("Foreign tax paid amount is required")
        
    if not data.get('foreign_income'):
        errors.append("Foreign source income is required")
        
    # Validate foreign tax documentation
    if not data.get('tax_documentation'):
        errors.append("Foreign tax documentation is required")
        
    return errors
        
@staticmethod
def _validate_postal_code(postal_code: str, country_code: str) -> bool:
    """Validate postal code format for specific country"""
    postal_formats = {
        'GB': r'^[A-Z]{1,2}[0-9][A-Z0-9]? ?[0-9][A-Z]{2}$',
        'CA': r'^[ABCEGHJKLMNPRSTVXY][0-9][ABCEGHJKLMNPRSTVWXYZ] ?[0-9][ABCEGHJKLMNPRSTVWXYZ][0-9]$',
        'JP': r'^[0-9]{3}-[0-9]{4}$'
    }
    
    if country_code not in postal_formats:
        return True  # Skip validation for countries without defined formats
        
    import re
    return bool(re.match(postal_formats[country_code], postal_code))

class ValidationRules:
    """Validation rules for tax forms"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.error_service = ErrorHandlingService()

    async def validate_1099_nec(data: Dict[str, Any]) -> List[str]:
        """Validate 1099-NEC specific rules"""
        errors = []
        
        # Check compensation threshold
        compensation = Decimal(str(data.get('payments', {}).get('nonemployee_compensation', 0)))
        if compensation < BusinessRules.NEC_THRESHOLD:
            errors.append(f"Nonemployee compensation must be ${BusinessRules.NEC_THRESHOLD} or more")
        
        # Validate state tax information
        state_info = data.get('state_tax_info', {})
        if state_info:
            errors.extend(BusinessRules.validate_state_withholding(state_info))

        # Validate TIN formats
        payer_tin = data.get('payer', {}).get('tin', '')
        recipient_tin = data.get('recipient', {}).get('tin', '')
        
        if not validate_tin_format(payer_tin):
            errors.append("Invalid payer TIN format")
        if not validate_tin_format(recipient_tin):
            errors.append("Invalid recipient TIN format")
        
        # Required fields validation
        required_fields = [
            ('payer.name', 'Payer name is required'),
            ('payer.tin', 'Payer TIN is required'),
            ('payer.address.street', 'Payer street address is required'),
            ('payer.address.city', 'Payer city is required'),
            ('payer.address.state', 'Payer state is required'),
            ('payer.address.zip_code', 'Payer ZIP code is required'),
            ('recipient.name', 'Recipient name is required'),
            ('recipient.tin', 'Recipient TIN is required'),
            ('recipient.address.street', 'Recipient street address is required'),
            ('recipient.address.city', 'Recipient city is required'),
            ('recipient.address.state', 'Recipient state is required'),
            ('recipient.address.zip_code', 'Recipient ZIP code is required'),
            ('payments.nonemployee_compensation', 'Nonemployee compensation is required')
        ]
        
        errors.extend(ValidationRules._check_required_fields(data, required_fields))
         
        # Use error handling service for validation errors
        if errors:
            await self.error_service.handle_error(
                ValidationError(errors),
                {
                    'form_type': '1099_NEC',
                    'validation_errors': errors
                },
                'VALIDATION'
            )
        
        return errors

    def validate_1099_k(data: Dict[str, Any]) -> List[str]:
        """Validate 1099-K specific rules"""
        errors = []
        
        # Check gross amount threshold
        gross_amount = Decimal(str(data.get('transactions', {}).get('gross_amount', 0)))
        if gross_amount < BusinessRules.K_THRESHOLD:
            errors.append(f"Gross amount must be ${BusinessRules.K_THRESHOLD} or more")
        
        # Check transaction count threshold
        transaction_count = int(data.get('transactions', {}).get('card_transactions', 0))
        if transaction_count < BusinessRules.K_TRANSACTION_THRESHOLD:
            errors.append(f"Must have {BusinessRules.K_TRANSACTION_THRESHOLD} or more transactions")

        # Validate monthly amounts
        monthly_amounts = {
            f'month_{i}': Decimal(str(data.get('transactions', {}).get(f'month_{i}', 0)))
            for i in range(1, 13)
        }
        if not BusinessRules.validate_monthly_amounts(monthly_amounts, gross_amount):
            errors.append("Sum of monthly amounts must equal gross amount")
        
        # Required fields for PSE
        pse_required_fields = [
            ('pse.name', 'PSE name is required'),
            ('pse.tin', 'PSE TIN is required'),
            ('pse.address.street', 'PSE street address is required'),
            ('pse.address.city', 'PSE city is required'),
            ('pse.address.state', 'PSE state is required'),
            ('pse.address.zip_code', 'PSE ZIP code is required')
        ]
        
        errors.extend(ValidationRules._check_required_fields(data, pse_required_fields))

        return errors

    def validate_1040ez(data: Dict[str, Any]) -> List[str]:
        """Validate 1040-EZ specific rules"""
        errors = []
        
        # Check income threshold
        total_income = Decimal(str(data.get('income', {}).get('total_income', 0)))
        if total_income > BusinessRules.EZ_INCOME_THRESHOLD:
            errors.append(f"Income must be less than ${BusinessRules.EZ_INCOME_THRESHOLD} to use Form 1040-EZ")
        
        # Check interest income
        interest = Decimal(str(data.get('income', {}).get('interest', 0)))
        if interest > 1500:
            errors.append("Interest income must be $1,500 or less to use Form 1040-EZ")
        
        # Required fields validation
        required_fields = [
            ('taxpayer.name', 'Taxpayer name is required'),
            ('taxpayer.ssn', 'Taxpayer SSN is required'),
            ('taxpayer.filing_status', 'Filing status is required'),
            ('income.wages', 'Wages amount is required'),
            ('tax_and_payments.federal_withheld', 'Federal tax withheld is required')
        ]
        
        errors.extend(ValidationRules._check_required_fields(data, required_fields))
        
        return errors

    def validate_schedule_b(data: Dict[str, Any]) -> List[str]:
        """Validate Schedule B specific rules"""
        errors = []
        
        # Validate interest payers
        interest_payers = data.get('interest', {}).get('payers', [])
        for payer in interest_payers:
            if not payer.get('name'):
                errors.append("Payer name is required for interest income")
            if not isinstance(payer.get('amount'), (int, float, Decimal)):
                errors.append("Valid amount is required for interest income")
        
        # Validate dividend payers
        dividend_payers = data.get('dividends', {}).get('payers', [])
        for payer in dividend_payers:
            if not payer.get('name'):
                errors.append("Payer name is required for dividend income")
            if not isinstance(payer.get('amount'), (int, float, Decimal)):
                errors.append("Valid amount is required for dividend income")
        
        # Validate foreign accounts
        if data.get('foreign_accounts', {}).get('has_foreign_accounts'):
            if not data.get('foreign_accounts', {}).get('countries'):
                errors.append("Countries must be specified for foreign accounts")
        
        return errors

    def validate_schedule_d(data: Dict[str, Any]) -> List[str]:
        """Validate Schedule D specific rules"""
        errors = []
        
        # Validate short-term transactions
        short_term = data.get('short_term', {}).get('transactions', [])
        for transaction in short_term:
            errors.extend(ValidationRules._validate_transaction(transaction, "short-term"))
        
        # Validate long-term transactions
        long_term = data.get('long_term', {}).get('transactions', [])
        for transaction in long_term:
            errors.extend(ValidationRules._validate_transaction(transaction, "long-term"))
        
        return errors

    def _validate_transaction(transaction: Dict[str, Any], trans_type: str) -> List[str]:
        """Validate individual transaction"""
        errors = []
        
        required_fields = [
            ('description', f'Description required for {trans_type} transaction'),
            ('date_acquired', f'Acquisition date required for {trans_type} transaction'),
            ('date_sold', f'Sale date required for {trans_type} transaction'),
            ('proceeds', f'Proceeds amount required for {trans_type} transaction'),
            ('cost_basis', f'Cost basis required for {trans_type} transaction')
        ]
        
        errors.extend(ValidationRules._check_required_fields(transaction, required_fields))
        return errors

    def validate_1040(data: Dict[str, Any]) -> List[str]:
        """Validate Form 1040 specific rules"""
        errors = []
        
        # Enhanced validation for schedules
        schedules = data.get('schedules', [])
        if schedules:
            # Validate Schedule C
            if 'SCHEDULE_C' in schedules:
                errors.extend(ValidationRules.validate_schedule_c(data))
                
            # Validate Schedule A
            if 'SCHEDULE_A' in schedules:
                errors.extend(ValidationRules.validate_schedule_a(data))
                
            # Validate Schedule B
            if 'SCHEDULE_B' in schedules:
                errors.extend(ValidationRules.validate_schedule_b(data))
                
            # Validate Schedule D
            if 'SCHEDULE_D' in schedules:
                errors.extend(ValidationRules.validate_schedule_d(data))
                
            # Validate Schedule F
            if 'SCHEDULE_F' in schedules:
                errors.extend(ValidationRules.validate_schedule_f(data))

        return errors

    def validate_schedule_f(data: Dict[str, Any]) -> List[str]:
        """Validate Schedule F specific rules"""
        errors = []
        warnings = []
        
        # Validate farm information
        farm_info = data.get('farm_info', {})
        
        # Enhanced validation for agricultural payments
        agricultural_payments = data.get('agricultural_payments', 0)
        commodity_payments = data.get('commodity_payments', 0)
        crop_insurance = data.get('crop_insurance', 0)
        
        if not farm_info.get('name'):
            errors.append("Farm name is required")
        if not farm_info.get('principal_product'):
            errors.append("Principal agricultural activity/product is required")
        if farm_info.get('accounting_method') not in valid_methods:
            errors.append("Invalid accounting method specified")
        
        # Validate inventory calculations
        inventory = data.get('inventory', {})
        if inventory:
            beginning = inventory.get('beginning', 0)
            ending = inventory.get('ending', 0)
            
            if ending < 0 or beginning < 0:
                errors.append("Inventory values cannot be negative")
                
            if abs(ending - beginning) > 500000:
                warnings.append("Large inventory change detected - please verify")

        # Validate agricultural payments
        if agricultural_payments > 0:
            if not data.get('agricultural_program_details'):
                warnings.append("Agricultural program details should be provided")

        # Validate crop insurance
        if crop_insurance > 0:
            if not data.get('crop_insurance_details'):
                warnings.append("Crop insurance details should be provided")

        # Validate commodity credit loans
        if commodity_payments > 0 and not data.get('commodity_loan_details'):
            warnings.append("Commodity loan details should be provided")

        return errors
