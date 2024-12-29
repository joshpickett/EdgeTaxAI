from typing import Dict, Any
import xml.etree.ElementTree as ElementTree
from decimal import Decimal
from .base_template import BaseMeFTemplate

class Form1099NECTemplate(BaseMeFTemplate):
    """Template for Form 1099-NEC XML generation"""
    
    def generate(self, data: Dict[str, Any]) -> str:
        """Generate Form 1099-NEC XML"""
        root = self.create_base_xml()
        self.add_header(root, data)
        
        # Add Form1099NEC
        form_1099nec = ElementTree.SubElement(root, 'Form1099NEC')
        
        # PayerInfo
        payer_info = ElementTree.SubElement(form_1099nec, 'PayerInfo')
        self._add_payer_info(payer_info, data)
        
        # RecipientInfo
        recipient_info = ElementTree.SubElement(form_1099nec, 'RecipientInfo')
        self._add_recipient_info(recipient_info, data)
        
        # PaymentInfo
        payment_info = ElementTree.SubElement(form_1099nec, 'PaymentInfo')
        self._add_payment_info(payment_info, data)
        
        # State Tax Info (if applicable)
        if data.get('state_tax_info'):
            state_tax = ElementTree.SubElement(form_1099nec, 'StateTaxInfo')
            self._add_state_tax_info(state_tax, data)
        
        xml_string = self.prettify_xml(root)
        
        # Validate against schema
        if not self.validate_xml(xml_string, '1099nec_2023v1.0.xsd'):
            raise ValueError("Generated XML failed schema validation")
            
        return xml_string
    
    def _add_payer_info(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add payer information section"""
        payer_data = data.get('payer', {})
        
        name = ElementTree.SubElement(parent, 'PayerName')
        name.text = payer_data.get('name', '')
        
        tin = ElementTree.SubElement(parent, 'PayerTIN')
        tin.text = payer_data.get('tin', '')
        
        address = ElementTree.SubElement(parent, 'PayerAddress')
        self._add_address(address, payer_data.get('address', {}))
        
        phone = ElementTree.SubElement(parent, 'PayerPhone')
        phone.text = payer_data.get('phone', '')
    
    def _add_recipient_info(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add recipient information section"""
        recipient_data = data.get('recipient', {})
        
        name = ElementTree.SubElement(parent, 'RecipientName')
        name.text = recipient_data.get('name', '')
        
        tin = ElementTree.SubElement(parent, 'RecipientTIN')
        tin.text = recipient_data.get('tin', '')
        
        address = ElementTree.SubElement(parent, 'RecipientAddress')
        self._add_address(address, recipient_data.get('address', {}))
        
        account_number = ElementTree.SubElement(parent, 'AccountNumber')
        account_number.text = recipient_data.get('account_number', '')
    
    def _add_payment_info(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add payment information section"""
        payment_data = data.get('payments', {})
        
        nonemployee_comp = ElementTree.SubElement(parent, 'NonemployeeCompensation')
        nonemployee_comp.text = str(payment_data.get('nonemployee_compensation', '0.00'))
        
        federal_tax_withheld = ElementTree.SubElement(parent, 'FederalTaxWithheld')
        federal_tax_withheld.text = str(payment_data.get('federal_tax_withheld', '0.00'))
        
        if payment_data.get('direct_sales') is not None:
            direct_sales = ElementTree.SubElement(parent, 'DirectSalesIndicator')
            direct_sales.text = str(payment_data['direct_sales']).lower()
    
    def _add_state_tax_info(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add state tax information section"""
        state_data = data.get('state_tax_info', {})
        
        state = ElementTree.SubElement(parent, 'State')
        state.text = state_data.get('state', '')
        
        state_identification_number = ElementTree.SubElement(parent, 'StateIdentificationNumber')
        state_identification_number.text = state_data.get('state_id', '')
        
        state_income = ElementTree.SubElement(parent, 'StateIncome')
        state_income.text = str(state_data.get('state_income', '0.00'))
        
        state_tax_withheld = ElementTree.SubElement(parent, 'StateTaxWithheld')
        state_tax_withheld.text = str(state_data.get('state_tax_withheld', '0.00'))
