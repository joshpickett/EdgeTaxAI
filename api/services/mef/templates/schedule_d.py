from typing import Dict, Any
import xml.etree.ElementTree as ElementTree
from decimal import Decimal
from .base_schedule_template import BaseScheduleTemplate

class ScheduleDTemplate(BaseScheduleTemplate):
    """Template for Schedule D (Capital Gains and Losses) XML generation"""
    
    def __init__(self):
        super().__init__()
        self.schedule_type = 'D'
    
    def _add_schedule_content(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add Schedule D specific content"""
        # Part I - Short-term Capital Gains and Losses
        short_term = ElementTree.SubElement(parent, 'ShortTermCapitalGains')
        self._add_short_term_transactions(short_term, data.get('short_term', {}))
        
        # Part II - Long-term Capital Gains and Losses
        long_term = ElementTree.SubElement(parent, 'LongTermCapitalGains')
        self._add_long_term_transactions(long_term, data.get('long_term', {}))
        
        # Part III - Summary
        summary = ElementTree.SubElement(parent, 'Summary')
        self._add_summary(summary, data.get('summary', {}))
    
    def _add_short_term_transactions(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add short-term transactions section"""
        transactions = ElementTree.SubElement(parent, 'Transactions')
        
        for transaction in data.get('transactions', []):
            trans = ElementTree.SubElement(transactions, 'Transaction')
            
            description = ElementTree.SubElement(trans, 'Description')
            description.text = transaction.get('description', '')
            
            date_acquired = ElementTree.SubElement(trans, 'DateAcquired')
            date_acquired.text = transaction.get('date_acquired', '')
            
            date_sold = ElementTree.SubElement(trans, 'DateSold')
            date_sold.text = transaction.get('date_sold', '')
            
            proceeds = ElementTree.SubElement(trans, 'Proceeds')
            proceeds.text = str(transaction.get('proceeds', '0.00'))
            
            cost_basis = ElementTree.SubElement(trans, 'CostBasis')
            cost_basis.text = str(transaction.get('cost_basis', '0.00'))
            
            gain_loss = ElementTree.SubElement(trans, 'GainLoss')
            gain_loss.text = str(transaction.get('gain_loss', '0.00'))
        
        # Totals
        totals = ElementTree.SubElement(parent, 'Totals')
        self._add_totals(totals, data.get('totals', {}))
    
    def _add_long_term_transactions(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add long-term transactions section"""
        transactions = ElementTree.SubElement(parent, 'Transactions')
        
        for transaction in data.get('transactions', []):
            trans = ElementTree.SubElement(transactions, 'Transaction')
            
            description = ElementTree.SubElement(trans, 'Description')
            description.text = transaction.get('description', '')
            
            date_acquired = ElementTree.SubElement(trans, 'DateAcquired')
            date_acquired.text = transaction.get('date_acquired', '')
            
            date_sold = ElementTree.SubElement(trans, 'DateSold')
            date_sold.text = transaction.get('date_sold', '')
            
            proceeds = ElementTree.SubElement(trans, 'Proceeds')
            proceeds.text = str(transaction.get('proceeds', '0.00'))
            
            cost_basis = ElementTree.SubElement(trans, 'CostBasis')
            cost_basis.text = str(transaction.get('cost_basis', '0.00'))
            
            gain_loss = ElementTree.SubElement(trans, 'GainLoss')
            gain_loss.text = str(transaction.get('gain_loss', '0.00'))
        
        # Totals
        totals = ElementTree.SubElement(parent, 'Totals')
        self._add_totals(totals, data.get('totals', {}))
    
    def _add_summary(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add summary section"""
        # Short-term totals
        short_term = ElementTree.SubElement(parent, 'ShortTermTotal')
        short_term.text = str(data.get('short_term_total', '0.00'))
        
        # Long-term totals
        long_term = ElementTree.SubElement(parent, 'LongTermTotal')
        long_term.text = str(data.get('long_term_total', '0.00'))
        
        # Net gain or loss
        net_gain_loss = ElementTree.SubElement(parent, 'NetGainLoss')
        net_gain_loss.text = str(data.get('net_gain_loss', '0.00'))
    
    def _add_totals(self, parent: ElementTree.Element, data: Dict[str, Any]) -> None:
        """Add totals section"""
        proceeds = ElementTree.SubElement(parent, 'TotalProceeds')
        proceeds.text = str(data.get('total_proceeds', '0.00'))
        
        cost_basis = ElementTree.SubElement(parent, 'TotalCostBasis')
        cost_basis.text = str(data.get('total_cost_basis', '0.00'))
        
        gain_loss = ElementTree.SubElement(parent, 'TotalGainLoss')
        gain_loss.text = str(data.get('total_gain_loss', '0.00'))
