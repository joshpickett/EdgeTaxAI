from typing import Dict, Any, Optional
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from api.models.database_models import FormProgress

class FormProgressManager:
    """Manage form progress and autosave"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.autosave_interval = 60  # seconds

    async def save_progress(
        self,
        user_id: int,
        form_type: str,
        progress_data: Dict[str, Any],
        db: Session
    ) -> None:
        """Save form progress"""
        try:
            progress = FormProgress(
                user_id=user_id,
                form_type=form_type,
                progress_data=progress_data,
                last_modified=datetime.utcnow()
            )
            
            db.merge(progress)
            db.commit()
            
        except Exception as e:
            self.logger.error(f"Error saving progress: {str(e)}")
            raise

    async def get_progress(
        self,
        user_id: int,
        form_type: str,
        db: Session
    ) -> Optional[Dict[str, Any]]:
        """Get saved progress"""
        try:
            progress = db.query(FormProgress).filter(
                FormProgress.user_id == user_id,
                FormProgress.form_type == form_type
            ).first()
            
            return progress.progress_data if progress else None
            
        except Exception as e:
            self.logger.error(f"Error getting progress: {str(e)}")
            raise

    async def clear_progress(
        self,
        user_id: int,
        form_type: str,
        db: Session
    ) -> None:
        """Clear saved progress"""
        try:
            db.query(FormProgress).filter(
                FormProgress.user_id == user_id,
                FormProgress.form_type == form_type
            ).delete()
            
            db.commit()
            
        except Exception as e:
            self.logger.error(f"Error clearing progress: {str(e)}")
            raise

    async def get_all_progress(
        self,
        user_id: int,
        db: Session
    ) -> Dict[str, Any]:
        """Get all saved progress for user"""
        try:
            progress_records = db.query(FormProgress).filter(
                FormProgress.user_id == user_id
            ).all()
            
            return {
                record.form_type: {
                    'data': record.progress_data,
                    'last_modified': record.last_modified.isoformat()
                }
                for record in progress_records
            }
            
        except Exception as e:
            self.logger.error(f"Error getting all progress: {str(e)}")
            raise

    def should_autosave(self, last_save: datetime) -> bool:
        """Check if autosave should trigger"""
        time_diff = (datetime.utcnow() - last_save).total_seconds()
        return time_diff >= self.autosave_interval
