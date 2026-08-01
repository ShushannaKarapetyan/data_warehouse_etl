import os
import logging
from sqlalchemy.exc import SQLAlchemyError
from src.db_connection import get_engine
from src.extract import extract_all
from src.transform_customers import transform_customers
from src.transform_products import transform_products
from src.transform_sales import transform_sales
from src.load import load_all

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(PROJECT_ROOT, "logs")
LOG_FILE = os.path.join(LOG_DIR, "etl_run.log")

os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_pipeline():
    logger.info("Starting ETL pipeline")

    try:
        engine = get_engine()
    except (RuntimeError, SQLAlchemyError) as e:
        logger.error(f"Aborting pipeline: could not establish database connection — {e}")
        return

    try:
        logger.info("Extracting source data...")
        raw_data = extract_all()

        logger.info("Transforming customers...")
        dim_customers = transform_customers(raw_data)
        print(dim_customers.head())

        logger.info("Transforming products...")
        dim_products = transform_products(raw_data)
        print(dim_products.head())

        logger.info("Transforming sales...")
        fact_sales = transform_sales(raw_data, dim_customers, dim_products)
        print(fact_sales.head())

        logger.info("Loading data into warehouse...")
        load_all(dim_customers, dim_products, fact_sales, engine)
        logger.info("Pipeline run complete")

    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        return

if __name__ == "__main__":
    run_pipeline()
