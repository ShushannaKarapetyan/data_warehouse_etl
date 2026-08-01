import logging
import pandas as pd

logger = logging.getLogger(__name__)

def _clean_crm_cust_info(df: pd.DataFrame) -> pd.DataFrame:
    """
    - drop rows with NULL cst_id
    - deduplicate, keeping the most recent record per customer
    - trim names
    - standardize marital status and gender
    """
    df = df.copy()

    # Drop NULL cst_id (equivalent of WHERE cst_id IS NOT NULL)
    df = df[df["cst_id"].notna()]

    # Deduplicate: keep the most recent row per cst_id
    # (equivalent of ROW_NUMBER() OVER (PARTITION BY cst_id ORDER BY cst_create_date DESC) = 1)
    df["cst_create_date"] = pd.to_datetime(df["cst_create_date"], errors="coerce")
    df = df.sort_values("cst_create_date", ascending=False)
    df = df.drop_duplicates(subset="cst_id", keep="first")

    # Trim whitespace on names
    df["cst_firstname"] = df["cst_firstname"].str.strip()
    df["cst_lastname"] = df["cst_lastname"].str.strip()

    # Standardize marital status
    df["cst_marital_status"] = (
        df["cst_marital_status"].str.upper().str.strip().map({"S": "Single", "M": "Married"})
        .fillna("n/a")
    )

    # Standardize gender
    df["cst_gndr"] = (
        df["cst_gndr"].str.upper().str.strip().map({"M": "Male", "F": "Female"})
        .fillna("n/a")
    )

    logger.info(f"Cleaned crm_cust_info: {len(df)} rows remain after dedup/null filtering")
    return df


def _clean_erp_cust_az12(df: pd.DataFrame) -> pd.DataFrame:
    """
    - strip 'NAS' prefix from cid
    - null out future birthdates
    - standardize gender
    """
    df = df.copy()

    df["cid"] = df["cid"].apply(lambda x: x[3:] if isinstance(x, str) and x.startswith("NAS") else x)

    df["bdate"] = pd.to_datetime(df["bdate"], errors="coerce")
    today = pd.Timestamp.now()
    df.loc[df["bdate"] > today, "bdate"] = pd.NaT

    df["gen"] = (
        df["gen"].str.upper().str.strip()
        .map({"F": "Female", "FEMALE": "Female", "M": "Male", "MALE": "Male"})
        .fillna("n/a")
    )

    return df

def _clean_erp_loc_a101(df: pd.DataFrame) -> pd.DataFrame:
    """
    - remove dashes from cid
    - standardize country names
    """
    df = df.copy()

    df["cid"] = df["cid"].str.replace("-", "", regex=False)

    def standardize_country(val):
        if pd.isna(val) or str(val).strip() == "":
            return "n/a"
        val = str(val).strip()
        if val == "DE":
            return "Germany"
        if val in ("US", "USA"):
            return "United States"
        return val

    df["cntry"] = df["cntry"].apply(standardize_country)

    return df


def transform_customers(raw_data: dict) -> pd.DataFrame:
    """
    Builds the final dim_customers DataFrame by cleaning
    crm_cust_info, erp_cust_az12, erp_loc_a101, then joining them together.
    """
    cust_info = _clean_crm_cust_info(raw_data["crm_cust_info"])
    cust_az12 = _clean_erp_cust_az12(raw_data["erp_cust_az12"])
    loc_a101 = _clean_erp_loc_a101(raw_data["erp_loc_a101"])

    # LEFT JOIN erp_cust_az12 ON ci.cst_key = ca.cid
    df = cust_info.merge(cust_az12, how="left", left_on="cst_key", right_on="cid", suffixes=("", "_az12"))

    # LEFT JOIN erp_loc_a101 ON ci.cst_key = la.cid
    df = df.merge(loc_a101, how="left", left_on="cst_key", right_on="cid", suffixes=("", "_loc"))

    # CRM is the master of gender info; fall back to ERP gender if CRM says 'n/a'
    df["gender"] = df.apply(
        lambda row: row["cst_gndr"] if row["cst_gndr"] != "n/a" else (row["gen"] if pd.notna(row["gen"]) else "n/a"),
        axis=1
    )

    # Generate surrogate key (equivalent of ROW_NUMBER() OVER (ORDER BY cst_id))
    df = df.sort_values("cst_id").reset_index(drop=True)
    df["customer_key"] = df.index + 1

    # Final column selection and renaming
    result = pd.DataFrame({
        "customer_key":    df["customer_key"],
        "customer_id":     df["cst_id"].astype(int),
        "customer_number": df["cst_key"],
        "first_name":      df["cst_firstname"],
        "last_name":       df["cst_lastname"],
        "country":         df["cntry"],
        "marital_status":  df["cst_marital_status"],
        "gender":          df["gender"],
        "birthdate":       df["bdate"],
        "create_date":     df["cst_create_date"],
    })

    logger.info(f"transform_customers produced {len(result)} rows")

    return result
