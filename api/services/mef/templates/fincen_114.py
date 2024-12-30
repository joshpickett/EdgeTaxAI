from typing import Dict, Any, List
import xml.etree.ElementTree as ElementTree
from decimal import Decimal
from .base_template import BaseMeFTemplate

class FinCEN114Template(BaseMeFTemplate):
    """Template for FinCEN Form 114 (FBAR) XML generation"""
    
    def __init__(self):
        super().__init__()
        self.form_type = 'FinCEN114'

    def generate(self, data: Dict[str, Any]) -> str:
        """Generate FinCEN 114 XML"""
        root = self.create_base_xml()
        self.add_header(root, data)
        
        # Add enhanced FBAR reporting
        form = ElementTree.SubElement(root, 'FinCEN114')
        
        # Add detailed account reporting
        accounts = ElementTree.SubElement(form, 'ForeignAccounts')
        self._add_foreign_accounts(accounts, data.get('accounts', []))
        
        # Add signature section with enhanced validation
        signature = ElementTree.SubElement(form, 'Signature')
        self._add_signature(signature, data.get('signature', {}))

        xml_string = self.prettify_xml(root)
        
        # Validate against schema
        if not self.validate_xml(xml_string, 'fincen114_2023v1.0.xsd'):
            raise ValueError("Generated XML failed schema validation")
            
        return xml_string

    def _add_filer_info(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add filer information"""
        # Personal information
        name = ElementTree.SubElement(parent, 'Name')
        name.text = data.get('name', '')
        
        social_security_number = ElementTree.SubElement(parent, 'SSN')
        social_security_number.text = data.get('ssn', '')
        
        address = ElementTree.SubElement(parent, 'Address')
        self._add_address(address, data.get('address', {}))
        
        # Filing type
        filing_type = ElementTree.SubElement(parent, 'FilingType')
        filing_type.text = data.get('filing_type', 'individual')
        
        # Contact information
        phone = ElementTree.SubElement(parent, 'Phone')
        phone.text = data.get('phone', '')
        
        email = ElementTree.SubElement(parent, 'Email')
        email.text = data.get('email', '')

    def _add_foreign_accounts(self, parent: ElementTree.Element, accounts: List[Dict[str, Any]]) -> None:
        """Add foreign accounts section"""
        for account in accounts:
            # Enhanced account validation
            if not self._validate_account_data(account):
                raise ValueError(f"Invalid account data: {account}")
            
            account_element = ElementTree.SubElement(parent, 'ForeignAccount')
            
            # Add detailed account information
            self._add_account_info(account_element, account)
            
            # Add account type classification
            account_type = ElementTree.SubElement(account_element, 'AccountType')
            account_type.text = self._classify_account_type(account)

            # Maximum value
            maximum_value = ElementTree.SubElement(account_element, 'MaximumValue')
            maximum_value.text = str(account.get('maximum_value', '0.00'))
            
            # Joint owners
            if account.get('joint_owners'):
                owners = ElementTree.SubElement(account_element, 'JointOwners')
                self._add_joint_owners(owners, account.get('joint_owners', []))

    def _add_institution_info(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add financial institution information"""
        name = ElementTree.SubElement(parent, 'Name')
        name.text = data.get('name', '')
        
        address = ElementTree.SubElement(parent, 'Address')
        self._add_address(address, data.get('address', {}))
        
        city = ElementTree.SubElement(parent, 'City')
        city.text = data.get('city', '')
        
        country = ElementTree.SubElement(parent, 'Country')
        country.text = data.get('country', '')

    def _add_account_info(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add account information"""
        number = ElementTree.SubElement(parent, 'AccountNumber')
        number.text = data.get('account_number', '')
        
        currency = ElementTree.SubElement(parent, 'Currency')
        currency.text = data.get('currency', '')
        
        opened_date = ElementTree.SubElement(parent, 'OpenedDate')
        opened_date.text = data.get('opened_date', '')
        
        closed_date = ElementTree.SubElement(parent, 'ClosedDate')
        closed_date.text = data.get('closed_date', '')

    def _add_joint_owners(self, parent: ElementTree.Element, owners: List[Dict[str, Any]]) -> None:
        """Add joint owners information"""
        for owner in owners:
            owner_element = ElementTree.SubElement(parent, 'JointOwner')
            
            name = ElementTree.SubElement(owner_element, 'Name')
            name.text = owner.get('name', '')
            
            taxpayer_identification_number = ElementTree.SubElement(owner_element, 'TIN')
            taxpayer_identification_number.text = owner.get('tin', '')
            
            address = ElementTree.SubElement(owner_element, 'Address')
            self._add_address(address, owner.get('address', {}))

    def _add_signature(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add signature information"""
        name = ElementTree.SubElement(parent, 'SignatureName')
        name.text = data.get('name', '')
        
        title = ElementTree.SubElement(parent, 'Title')
        title.text = data.get('title', '')
        
        date_signed = ElementTree.SubElement(parent, 'DateSigned')
        date_signed.text = data.get('date', '')
