import logging
from api.config.database import engine, Base
from api.models.users import Users
from api.models.personal_information import PersonalInformation
from api.models.income import Income
from api.models.expenses import Expenses
from api.models.tax_payments import TaxPayments

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db():
    """Initialize the database by creating all tables"""
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Successfully created all database tables")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


if __name__ == "__main__":
    logger.info("Starting database initialization...")
    init_db()
    logger.info("Database initialization completed")
