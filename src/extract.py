import os
import logging
import pandas as pd

logger = logging.getLogger(__name__)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def read_csv(file_path: str) -> pd.DataFrame:
    """
    Reads a CSV file into a DataFrame with basic error handling and logging.
    Raises FileNotFoundError or pd.errors.ParserError if something goes wrong.
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        df = pd.read_csv(file_path)
        df.columns = df.columns.str.strip().str.lower()   # normalize headers: CID -> cid, etc.
        logger.info(f"Read {len(df)} rows from {file_path}")
        return df
    except pd.errors.ParserError as e:
        logger.error(f"Failed to parse {file_path}: {e}")
        raise

def extract_all(base_path: str = None) -> dict:
    if base_path is None:
        base_path = os.path.join(PROJECT_ROOT, "datasets")

    paths = {
        "crm_cust_info":     os.path.join(base_path, "source_crm", "cust_info.csv"),
        "crm_prd_info":      os.path.join(base_path, "source_crm", "prd_info.csv"),
        "crm_sales_details": os.path.join(base_path, "source_crm", "sales_details.csv"),
        "erp_cust_az12":     os.path.join(base_path, "source_erp", "CUST_AZ12.csv"),
        "erp_loc_a101":      os.path.join(base_path, "source_erp", "LOC_A101.csv"),
        "erp_px_cat_g1v2":   os.path.join(base_path, "source_erp", "PX_CAT_G1V2.csv"),
    }

    dataframes = {}
    for key, path in paths.items():
        dataframes[key] = read_csv(path)

    return dataframes
