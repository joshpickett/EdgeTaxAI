from typing import Dict, List, Tuple, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from api.models.mileage import Mileage, RecurringTrip
from api.models.expenses import Expenses
from api.models.deductions import Deductions, DeductionType
from api.utils.trip_analyzer import TripAnalyzer
from api.config.tax_config import TAX_CONFIG
from api.utils.error_handler import APIError


class MileageService:
    def __init__(self, db: Session):
        self.db = db
        self.trip_analyzer = TripAnalyzer()

    def create_mileage_record(self, data: Dict) -> Tuple[Mileage, Expenses, Deductions]:
        """Create a new mileage record with associated expense and deduction"""
        try:
            # Calculate distance
            distance, error = self.trip_analyzer.calculate_trip_distance(
                data["start_location"], data["end_location"]
            )

            if error:
                raise APIError(f"Failed to calculate distance: {error}")

            # Create mileage record
            mileage = Mileage(
                user_id=data["user_id"],
                start_location=data["start_location"],
                end_location=data["end_location"],
                distance=distance,
                date=data["date"],
                purpose=data.get("purpose"),
            )

            # Calculate deduction amount
            deduction_amount = distance * TAX_CONFIG["IRS_MILEAGE_RATE"]

            # Create expense record
            expense = Expenses(
                user_id=data["user_id"],
                amount=deduction_amount,
                description=f"Mileage: {data['start_location']} to {data['end_location']}",
                category="TRAVEL",
                date=data["date"],
            )

            # Create deduction record
            deduction = Deductions(
                user_id=data["user_id"],
                type=DeductionType.MILEAGE,
                amount=deduction_amount,
                description=f"Mileage deduction: {distance} miles",
                tax_year=datetime.strptime(data["date"], "%Y-%m-%d").year,
            )

            self.db.add_all([mileage, expense, deduction])
            self.db.commit()

            return mileage, expense, deduction

        except Exception as e:
            self.db.rollback()
            raise APIError(f"Failed to create mileage record: {str(e)}")

    def get_mileage_summary(self, user_id: int, year: int) -> Dict:
        """Get summary of mileage records for a specific year"""
        try:
            records = (
                self.db.query(Mileage)
                .filter(
                    Mileage.user_id == user_id, extract("year", Mileage.date) == year
                )
                .all()
            )

            total_miles = sum(record.distance for record in records)
            total_deduction = total_miles * TAX_CONFIG["IRS_MILEAGE_RATE"]

            return {
                "year": year,
                "total_miles": total_miles,
                "total_trips": len(records),
                "total_deduction": total_deduction,
                "rate_used": TAX_CONFIG["IRS_MILEAGE_RATE"],
            }

        except Exception as e:
            raise APIError(f"Failed to get mileage summary: {str(e)}")

    def create_recurring_trip(self, data: Dict) -> RecurringTrip:
        """Create a new recurring trip pattern"""
        try:
            recurring_trip = RecurringTrip(
                user_id=data["user_id"],
                start_location=data["start_location"],
                end_location=data["end_location"],
                frequency=data["frequency"],
                purpose=data.get("purpose"),
            )

            self.db.add(recurring_trip)
            self.db.commit()

            return recurring_trip

        except Exception as e:
            self.db.rollback()
            raise APIError(f"Failed to create recurring trip: {str(e)}")
