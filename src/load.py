import logging
import pandas as pd
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

def load_dataframe(df: pd.DataFrame, table_name: str, engine) -> None:
    """
    Truncates the target table, then loads the DataFrame into it.
    Truncate + insert (append) is used instead of to_sql's if_exists='replace'
    so the table structure/constraints defined in the DDL are preserved.
    """
    try:
        with engine.begin() as conn:
            # FK constraints prevent truncating dim tables while fact_sales
            # still references them, so disable checks for the duration
            # of this single transaction, then re-enable.
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
            conn.execute(text(f"TRUNCATE TABLE {table_name}"))
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))

        df.to_sql(table_name, engine, if_exists="append", index=False)
        logger.info(f"Loaded {len(df)} rows into {table_name}")

    except SQLAlchemyError as e:
        logger.error(f"Failed to load {table_name}: {e}")
        raise

def load_all(dim_customers: pd.DataFrame, dim_products: pd.DataFrame, fact_sales: pd.DataFrame, engine) -> None:
    """
    Loads all tables in the correct order: dimensions first,
    then the fact table, since fact_sales has FK references to both.
    """
    load_dataframe(dim_customers, "dim_customers", engine)
    load_dataframe(dim_products, "dim_products", engine)
    load_dataframe(fact_sales, "fact_sales", engine)
