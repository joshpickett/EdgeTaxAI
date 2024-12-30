from typing import Dict, Any, List
import logging
from datetime import datetime
from api.services.mef.cross_schedule_calculator import CrossScheduleCalculator
from api.services.mef.schedule_management_service import ScheduleManagementService

class FormScheduleService:
    """Service for managing form schedules"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cross_calculator = CrossScheduleCalculator()
        self.schedule_manager = ScheduleManagementService()

    async def generate_summary(
        self,
        user_id: int,
        tax_year: int
    ) -> Dict[str, Any]:
        """Generate schedule summary for form"""
        try:
            # Get required schedules
            required_schedules = await self.schedule_manager.determine_required_schedules(
                user_id, tax_year
            )
            
            # Generate schedule data
            schedule_data = {}
            for schedule in required_schedules:
                schedule_data[schedule] = await self.schedule_manager.generate_schedule(
                    schedule,
                    {'user_id': user_id, 'tax_year': tax_year}
                )
            
            # Calculate cross-schedule totals
            totals = await self.cross_calculator.calculate_totals(schedule_data)
            
            # Validate consistency
            validation = await self.cross_calculator.validate_consistency(schedule_data)
            
            return {
                'required_schedules': required_schedules,
                'schedule_data': schedule_data,
                'totals': totals,
                'validation': validation,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error generating schedule summary: {str(e)}")
            raise

    async def validate_schedule(
        self,
        schedule_type: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate schedule data"""
        try:
            validation_result = await self.schedule_manager.validate_schedule_completeness(
                schedule_type, data
            )
            
            return {
                'is_valid': validation_result['is_valid'],
                'errors': validation_result.get('errors', []),
                'warnings': validation_result.get('warnings', []),
                'missing_fields': validation_result.get('missing_fields', [])
            }
            
        except Exception as e:
            self.logger.error(f"Error validating schedule: {str(e)}")
            raise

    async def optimize_schedule_order(
        self,
        schedules: List[str]
    ) -> List[str]:
        """Optimize schedule processing order"""
        try:
            return await self.schedule_manager.optimize_schedule_order(schedules)
        except Exception as e:
            self.logger.error(f"Error optimizing schedule order: {str(e)}")
            raise

    async def get_schedule_dependencies(
        self,
        schedule_type: str
    ) -> Dict[str, Any]:
        """Get schedule dependencies"""
        try:
            dependencies = await self.schedule_manager.validate_schedule_dependencies(
                [schedule_type]
            )
            
            return {
                'dependencies': dependencies.get('missing_dependencies', []),
                'invalid_combinations': dependencies.get('invalid_combinations', [])
            }
            
        except Exception as e:
            self.logger.error(f"Error getting schedule dependencies: {str(e)}")
            raise

    async def calculate_cross_schedule_totals(
        self,
        schedules: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate totals across multiple schedules"""
        try:
            return await self.cross_calculator.calculate_totals(schedules)
        except Exception as e:
            self.logger.error(f"Error calculating cross-schedule totals: {str(e)}")
            raise

    async def validate_cross_schedule_consistency(
        self,
        schedules: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate consistency between related schedules"""
        try:
            return await self.cross_calculator.validate_consistency(schedules)
        except Exception as e:
            self.logger.error(f"Error validating cross-schedule consistency: {str(e)}")
            raise
