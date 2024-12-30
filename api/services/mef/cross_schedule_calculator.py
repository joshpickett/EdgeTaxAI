from typing import Dict, Any
import logging
from decimal import Decimal

class CrossScheduleCalculator:
    """Handle calculations across multiple schedules"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def calculate_totals(self, schedules: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate totals across all schedules"""
        try:
            totals = {
                'total_income': Decimal('0'),
                'total_expenses': Decimal('0'),
                'total_deductions': Decimal('0'),
                'net_profit_loss': Decimal('0')
            }

            # Process Schedule C
            if 'SCHEDULE_C' in schedules:
                schedule_c = schedules['SCHEDULE_C']
                totals['total_income'] += self._calculate_schedule_c_income(schedule_c)
                totals['total_expenses'] += self._calculate_schedule_c_expenses(schedule_c)

            # Process Schedule E
            if 'SCHEDULE_E' in schedules:
                schedule_e = schedules['SCHEDULE_E']
                totals['total_income'] += self._calculate_schedule_e_income(schedule_e)
                totals['total_expenses'] += self._calculate_schedule_e_expenses(schedule_e)

            # Calculate net profit/loss
            totals['net_profit_loss'] = totals['total_income'] - totals['total_expenses']

            return totals

        except Exception as e:
            self.logger.error(f"Error calculating cross-schedule totals: {str(e)}")
            raise

    async def validate_consistency(self, schedules: Dict[str, Any]) -> Dict[str, Any]:
        """Validate consistency between related schedules"""
        try:
            validation_results = {
                'is_valid': True,
                'inconsistencies': []
            }

            # Validate Schedule C and SE consistency
            if 'SCHEDULE_C' in schedules and 'SCHEDULE_SE' in schedules:
                self._validate_c_se_consistency(
                    schedules['SCHEDULE_C'],
                    schedules['SCHEDULE_SE'],
                    validation_results
                )

            # Validate Schedule E and related forms
            if 'SCHEDULE_E' in schedules:
                self._validate_schedule_e_consistency(
                    schedules['SCHEDULE_E'],
                    validation_results
                )

            return validation_results

        except Exception as e:
            self.logger.error(f"Error validating schedule consistency: {str(e)}")
            raise

    def _calculate_schedule_c_income(self, schedule: Dict[str, Any]) -> Decimal:
        """Calculate total income from Schedule C"""
        income = schedule.get('income', {})
        return sum(Decimal(str(amount)) for amount in income.values())

    def _calculate_schedule_c_expenses(self, schedule: Dict[str, Any]) -> Decimal:
        """Calculate total expenses from Schedule C"""
        expenses = schedule.get('expenses', {})
        return sum(Decimal(str(amount)) for amount in expenses.values())

    def _calculate_schedule_e_income(self, schedule: Dict[str, Any]) -> Decimal:
        """Calculate total income from Schedule E"""
        total = Decimal('0')
        for property_data in schedule.get('properties', []):
            income = property_data.get('income', {})
            total += sum(Decimal(str(amount)) for amount in income.values())
        return total

    def _calculate_schedule_e_expenses(self, schedule: Dict[str, Any]) -> Decimal:
        """Calculate total expenses from Schedule E"""
        total = Decimal('0')
        for property_data in schedule.get('properties', []):
            expenses = property_data.get('expenses', {})
            total += sum(Decimal(str(amount)) for amount in expenses.values())
        return total

    def _validate_c_se_consistency(
        self,
        schedule_c: Dict[str, Any],
        schedule_se: Dict[str, Any],
        validation_results: Dict[str, Any]
    ) -> None:
        """Validate consistency between Schedule C and SE"""
        c_net_profit = self._calculate_schedule_c_income(schedule_c) - \
                      self._calculate_schedule_c_expenses(schedule_c)
        se_income = Decimal(str(schedule_se.get('self_employment_income', 0)))

        if abs(c_net_profit - se_income) > Decimal('0.01'):
            validation_results['is_valid'] = False
            validation_results['inconsistencies'].append({
                'type': 'schedule_c_se_mismatch',
                'message': 'Schedule C net profit does not match Schedule SE income',
                'schedule_c_amount': str(c_net_profit),
                'schedule_se_amount': str(se_income)
            })

    def _validate_schedule_e_consistency(
        self,
        schedule_e: Dict[str, Any],
        validation_results: Dict[str, Any]
    ) -> None:
        """Validate Schedule E internal consistency"""
        for idx, property_data in enumerate(schedule_e.get('properties', [])):
            if not self._validate_property_data(property_data):
                validation_results['is_valid'] = False
                validation_results['inconsistencies'].append({
                    'type': 'schedule_e_property_incomplete',
                    'message': f'Property {idx + 1} has incomplete or invalid data',
                    'property_index': idx
                })

    def _validate_property_data(self, property_data: Dict[str, Any]) -> bool:
        """Validate individual property data in Schedule E"""
        required_fields = ['address', 'type', 'income', 'expenses']
        return all(field in property_data for field in required_fields)
