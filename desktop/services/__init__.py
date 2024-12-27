"""
Desktop Services Package
Contains service adapters for interfacing with backend services
"""
from desktop.setup_path import setup_desktop_path
setup_desktop_path()

from .ai_service_adapter import AIServiceAdapter
from .bank_service_adapter import BankServiceAdapter
from .expense_service_adapter import ExpenseServiceAdapter
from .sync_service_adapter import SyncServiceAdapter

__all__ = [
    'AIServiceAdapter',
    'BankServiceAdapter',
    'ExpenseServiceAdapter',
    'SyncServiceAdapter'
]
