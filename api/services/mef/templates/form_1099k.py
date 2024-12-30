from typing import Dict, Any
import xml.etree.ElementTree as ElementTree
from decimal import Decimal
from .base_template import BaseMeFTemplate 
from shared.types.tax_forms import Form1099KECData

class Form1099KTemplate(BaseMeFTemplate):
    """Template for Form 1099-K XML generation"""
    
    def __init__(self):
        super().__init__()
        self.form_type = 'Form1099K'

    def generate(self, data: Dict[str, Any]) -> str:
        """Generate Form 1099-K XML"""
        root = self.create_base_xml()
        self.add_header(root, data)
        
        # Add form metadata
        self._add_form_metadata(root, data.get('formMetadata', {}))
        
        # Add Form1099K
        form_1099k = ElementTree.SubElement(root, 'Form1099K')
        
        # PaymentSettlementEntity Info
        payment_settlement_entity_info = ElementTree.SubElement(form_1099k, 'PaymentSettlementEntityInfo')
        self._add_payment_settlement_entity_info(payment_settlement_entity_info, data)
        
        # PayeeInfo
        payee_info = ElementTree.SubElement(form_1099k, 'PayeeInfo')
        self._add_payee_info(payee_info, data)
        
        # TransactionInfo
        transaction_info = ElementTree.SubElement(form_1099k, 'TransactionInfo')
        self._add_transaction_info(transaction_info, data)
        
        # State Tax Info (if applicable)
        if data.get('state_tax_info'):
            state_tax_info = ElementTree.SubElement(form_1099k, 'StateTaxInfo')
            self._add_state_tax_info(state_tax_info, data)
        
        xml_string = self.prettify_xml(root)
        
        # Validate against schema
        if not self.validate_xml(xml_string, '1099k_2023v1.0.xsd'):
            raise ValueError("Generated XML failed schema validation")
            
        return xml_string
    
    def _add_payment_settlement_entity_info(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add payment settlement entity information"""
        payment_settlement_entity_data = data.get('pse', {})
        
        name = ElementTree.SubElement(parent, 'PSEName')
        name.text = payment_settlement_entity_data.get('name', '')
        
        tin = ElementTree.SubElement(parent, 'PSETIN')
        tin.text = payment_settlement_entity_data.get('tin', '')
        
        address = ElementTree.SubElement(parent, 'PSEAddress')
        self._add_address(address, payment_settlement_entity_data.get('address', {}))
        
        phone = ElementTree.SubElement(parent, 'PSEPhone')
        phone.text = payment_settlement_entity_data.get('phone', '')
    
    def _add_form_metadata(self, parent: ElementTree.Element, metadata: Dict[str, Any]) -> None:
        """Add form metadata"""
        if not metadata:
            return
            
        form_meta = ElementTree.SubElement(parent, 'FormMetadata')
        
        tax_year = ElementTree.SubElement(form_meta, 'TaxYear')
        tax_year.text = str(metadata.get('taxYear', ''))
        
        corrected = ElementTree.SubElement(form_meta, 'Corrected')
        corrected.text = str(metadata.get('corrected', False)).lower()
    
    def _add_payee_info(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add payee information"""
        payee_data = data.get('payee', {})
        
        name = ElementTree.SubElement(parent, 'PayeeName')
        name.text = payee_data.get('name', '')
        
        tin = ElementTree.SubElement(parent, 'PayeeTIN')
        tin.text = payee_data.get('tin', '')
        
        address = ElementTree.SubElement(parent, 'PayeeAddress')
        self._add_address(address, payee_data.get('address', {}))
        
        account_number = ElementTree.SubElement(parent, 'AccountNumber')
        account_number.text = payee_data.get('account_number', '')
    
    def _add_transaction_info(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add transaction information"""
        transaction_data = data.get('transactions', {})
        
        # Add transaction totals
        gross_amount = ElementTree.SubElement(parent, 'GrossAmount')
        gross_amount.text = str(transaction_data.get('grossAmount', '0.00'))
        
        card_not_present = ElementTree.SubElement(parent, 'CardNotPresent')
        card_not_present.text = str(transaction_data.get('cardNotPresent', '0.00'))
        
        payment_card = ElementTree.SubElement(parent, 'PaymentCardTransactions')
        payment_card.text = str(transaction_data.get('paymentCardTransactions', '0.00'))
        
        third_party = ElementTree.SubElement(parent, 'ThirdPartyNetwork')
        third_party.text = str(transaction_data.get('thirdPartyNetwork', '0.00'))
        
        # Add monthly amounts
        monthly = ElementTree.SubElement(parent, 'MonthlyAmounts')
        for month, amount in transaction_data.get('monthlyAmounts', {}).items():
            month_elem = ElementTree.SubElement(monthly, month)
            month_elem.text = str(amount)
        
        federal_tax_withheld = ElementTree.SubElement(parent, 'FederalTaxWithheld')
        federal_tax_withheld.text = str(transaction_data.get('federalTaxWithheld', '0.00'))
    
    def _add_state_tax_info(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add state tax information"""
        state_tax_data = data.get('state_tax_info', {})
        
        state = ElementTree.SubElement(parent, 'State')
        state.text = state_tax_data.get('state', '')
        
        state_identification_number = ElementTree.SubElement(parent, 'StateIdentificationNumber')
        state_identification_number.text = state_tax_data.get('state_id', '')
        
        state_income = ElementTree.SubElement(parent, 'StateIncome')
        state_income.text = str(state_tax_data.get('state_income', '0.00'))
        
        state_tax_withheld = ElementTree.SubElement(parent, 'StateTaxWithheld')
        state_tax_withheld.text = str(state_tax_data.get('state_tax_withheld', '0.00'))
