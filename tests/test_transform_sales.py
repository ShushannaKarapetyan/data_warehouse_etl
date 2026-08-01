import pandas as pd
from src.transform_sales import _clean_crm_sales_details

def test_invalid_date_becomes_null():
    df = pd.DataFrame({
        "sls_ord_num": ["SO1"],
        "sls_prd_key": ["HL-U509"],
        "sls_cust_id": [1],
        "sls_order_dt": [0],            #invalid order date
        "sls_ship_dt": [2025101],       #invalid: wrong length (7 digits)
        "sls_due_dt": [20251015],       #valid
        "sls_sales": [100],
        "sls_quantity": [2],
        "sls_price": [50],
    })
    result = _clean_crm_sales_details(df)

    assert pd.isna(result.iloc[0]["sls_order_dt"])
    assert pd.isna(result.iloc[0]["sls_ship_dt"])
    assert result.iloc[0]["sls_due_dt"] == pd.Timestamp("2025-10-15")

def test_sales_recalculated_when_inconsistent():
    df = pd.DataFrame({
        "sls_ord_num": ["SO1"],
        "sls_prd_key": ["HL-U509"],
        "sls_cust_id": [1],
        "sls_order_dt": [20250101],
        "sls_ship_dt": [20250102],
        "sls_due_dt": [20250103],
        "sls_sales": [999],   #wrong: doesn't match qty * price
        "sls_quantity": [2],
        "sls_price": [50],
    })
    result = _clean_crm_sales_details(df)

    assert result.iloc[0]["sls_sales"] == 100  #2 * 50

def test_price_recalculated_when_invalid():
    df = pd.DataFrame({
        "sls_ord_num": ["SO1"],
        "sls_prd_key": ["HL-U509"],
        "sls_cust_id": [1],
        "sls_order_dt": [20250101],
        "sls_ship_dt": [20250102],
        "sls_due_dt": [20250103],
        "sls_sales": [100],
        "sls_quantity": [2],
        "sls_price": [-5],  #invalid: not equal to 50 or -50
    })
    result = _clean_crm_sales_details(df)

    assert result.iloc[0]["sls_price"] == 50
