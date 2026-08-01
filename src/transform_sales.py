import logging
import pandas as pd

logger = logging.getLogger(__name__)

def _clean_crm_sales_details(df: pd.DataFrame) -> pd.DataFrame:
    """
    - parse sls_order_dt / sls_ship_dt / sls_due_dt from YYYYMMDD ints,
      treating 0 or wrong-length values as invalid -> NULL
    - recalculate sls_sales if missing/invalid/inconsistent with qty * price
    - recalculate sls_price if missing/invalid
    """
    df = df.copy()

    def parse_yyyymmdd(series: pd.Series) -> pd.Series:
        # CASE WHEN val = 0 OR LENGTH(val) != 8 THEN NULL ELSE STR_TO_DATE(val, '%Y%m%d') END
        s = series.astype("Int64").astype(str)
        s = s.where((series != 0) & (s.str.len() == 8), other=pd.NA)
        return pd.to_datetime(s, format="%Y%m%d", errors="coerce")

    df["sls_order_dt"] = parse_yyyymmdd(df["sls_order_dt"])
    df["sls_ship_dt"] = parse_yyyymmdd(df["sls_ship_dt"])
    df["sls_due_dt"] = parse_yyyymmdd(df["sls_due_dt"])

    original_sales = df["sls_sales"]
    original_price = df["sls_price"]

    recalculated_sales = df["sls_quantity"] * original_price.abs()
    invalid_sales = (
            original_sales.isna()
            | (original_sales <= 0)
            | (original_sales != recalculated_sales)
    )
    df["sls_sales"] = original_sales.where(~invalid_sales, recalculated_sales)

    invalid_price = original_price.isna() | (original_price <= 0)
    recalculated_price = original_sales / df["sls_quantity"].replace(0, pd.NA)
    df["sls_price"] = original_price.where(~invalid_price, recalculated_price)

    logger.info(f"Cleaned crm_sales_details: {len(df)} rows")
    return df

def transform_sales(raw_data: dict, dim_customers: pd.DataFrame, dim_products: pd.DataFrame) -> pd.DataFrame:
    """
    Builds the final fact_sales DataFrame by cleaning
    crm_sales_details, then looking up customer_key and product_key
    from the already-built dimension tables.
    """
    sales = _clean_crm_sales_details(raw_data["crm_sales_details"])

    # LEFT JOIN dim_products pr ON sd.sls_prd_key = pr.product_number
    df = sales.merge(
        dim_products[["product_key", "product_number"]],
        how="left", left_on="sls_prd_key", right_on="product_number"
    )

    # LEFT JOIN dim_customers cu ON sd.sls_cust_id = cu.customer_id
    df = df.merge(
        dim_customers[["customer_key", "customer_id"]],
        how="left", left_on="sls_cust_id", right_on="customer_id"
    )

    # Final column selection and renaming
    result = pd.DataFrame({
        "order_number":  df["sls_ord_num"],
        "product_key":   df["product_key"],
        "customer_key":  df["customer_key"],
        "order_date":    df["sls_order_dt"],
        "shipping_date": df["sls_ship_dt"],
        "due_date":      df["sls_due_dt"],
        "sales":         df["sls_sales"],
        "quantity":      df["sls_quantity"],
        "price":         df["sls_price"],
    })

    logger.info(f"transform_sales produced {len(result)} rows")

    # Sanity check: flag any rows where the key lookup failed (orphaned references)
    unmatched_products = result["product_key"].isna().sum()
    unmatched_customers = result["customer_key"].isna().sum()
    if unmatched_products:
        logger.warning(f"{unmatched_products} sales rows have no matching product_key")
    if unmatched_customers:
        logger.warning(f"{unmatched_customers} sales rows have no matching customer_key")

    return result
