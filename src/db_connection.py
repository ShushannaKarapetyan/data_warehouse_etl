import os
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

load_dotenv()

def get_engine():
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    database = os.getenv("DB_NAME")

    missing = [name for name, val in [
        ("DB_HOST", host), ("DB_PORT", port), ("DB_USER", user),
        ("DB_PASSWORD", password), ("DB_NAME", database)
    ] if not val]

    if missing:
        logger.error(f"Missing required environment variables: {', '.join(missing)}")
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")

    connection_string = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"
    engine = create_engine(connection_string)
    logger.info(f"Engine created for database '{database}' at {host}:{port}")
    return engine

def test_connection(engine):
    try:
        with engine.connect() as conn:
            logger.info("Database connection successful")
            return True
    except SQLAlchemyError as e:
        logger.error(f"Database connection failed: {e}")
        return False
