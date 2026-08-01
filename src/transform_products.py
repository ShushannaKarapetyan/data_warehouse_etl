import logging
import pandas as pd

logger = logging.getLogger(__name__)

def _clean_crm_prd_info(df: pd.DataFrame) -> pd.DataFrame:
    """
    - extract cat_id from prd_key (first 5 chars, dashes -> underscores)
    - strip cat_id prefix from prd_key itself
    - default NULL prd_cost to 0
    - map prd_line codes to full names
    - calculate prd_end_dt as (next start date for same prd_key) - 1 day
    """
    df = df.copy()

    # REPLACE(SUBSTRING(prd_key, 1, 5), '-', '_') AS cat_id
    df["cat_id"] = df["prd_key"].str[:5].str.replace("-", "_", regex=False)

    # SUBSTRING(prd_key, 7, LENGTH(prd_key)) AS prd_key
    df["prd_key"] = df["prd_key"].str[6:]

    # IFNULL(prd_cost, 0)
    df["prd_cost"] = df["prd_cost"].fillna(0)

    # CASE UPPER(TRIM(prd_line)) WHEN 'M' THEN 'Mountain' ... ELSE 'n/a'
    df["prd_line"] = (
        df["prd_line"].str.upper().str.strip()
        .map({"M": "Mountain", "R": "Road", "S": "Other Sales", "T": "Touring"})
        .fillna("n/a")
    )

    # CAST(prd_start_dt AS DATE)
    df["prd_start_dt"] = pd.to_datetime(df["prd_start_dt"], errors="coerce")

    # LEAD(prd_start_dt) OVER (PARTITION BY prd_key ORDER BY prd_start_dt) - INTERVAL 1 DAY
    df = df.sort_values(["prd_key", "prd_start_dt"])
    df["prd_end_dt"] = df.groupby("prd_key")["prd_start_dt"].shift(-1) - pd.Timedelta(days=1)

    logger.info(f"Cleaned crm_prd_info: {len(df)} rows")
    return df

def _clean_erp_px_cat_g1v2(df: pd.DataFrame) -> pd.DataFrame:
    """
    - straight passthrough, no transformation needed
    """
    return df.copy()

def transform_products(raw_data: dict) -> pd.DataFrame:
    """
    Builds the final gold.dim_products-equivalent DataFrame by cleaning
    crm_prd_info and erp_px_cat_g1v2, then joining them together.
    """
    prd_info = _clean_crm_prd_info(raw_data["crm_prd_info"])
    px_cat = _clean_erp_px_cat_g1v2(raw_data["erp_px_cat_g1v2"])

    # LEFT JOIN erp_px_cat_g1v2 pc ON pn.cat_id = pc.id
    df = prd_info.merge(px_cat, how="left", left_on="cat_id", right_on="id", suffixes=("", "_cat"))

    # WHERE prd_end_dt IS NULL -- Filter out historical data (keep only current/active products)
    df = df[df["prd_end_dt"].isna()]

    # ROW_NUMBER() OVER (ORDER BY prd_start_dt, prd_key)
    df = df.sort_values(["prd_start_dt", "prd_key"]).reset_index(drop=True)
    df["product_key"] = df.index + 1

    # Final column selection and renaming
    result = pd.DataFrame({
        "product_key":     df["product_key"],
        "product_id":      df["prd_id"],
        "product_number":  df["prd_key"],
        "product_name":    df["prd_nm"],
        "category_id":     df["cat_id"],
        "category":        df["cat"],
        "subcategory":     df["subcat"],
        "maintenance":     df["maintenance"],
        "cost":            df["prd_cost"],
        "product_line":    df["prd_line"],
        "start_date":      df["prd_start_dt"],
    })

    logger.info(f"transform_products produced {len(result)} rows")

    return result
