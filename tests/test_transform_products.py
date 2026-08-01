import pandas as pd
from src.transform_products import _clean_crm_prd_info

def make_prd_info_df(**overrides):
    base = {
        "prd_id": [1],
        "prd_key": ["AC-HE-HL-U509"],
        "prd_nm": ["Product A"],
        "prd_cost": [25.0],
        "prd_line": ["m"],
        "prd_start_dt": ["2023-01-01"],
    }
    base.update(overrides)

    return pd.DataFrame(base)

def test_cat_id_extraction():
    df = make_prd_info_df()
    result = _clean_crm_prd_info(df)

    assert result.iloc[0]["cat_id"] == "AC_HE"

def test_prd_key_strips_category_prefix():
    df = make_prd_info_df()
    result = _clean_crm_prd_info(df)

    assert result.iloc[0]["prd_key"] == "HL-U509"

def test_null_cost_defaults_to_zero():
    df = make_prd_info_df(prd_cost=[None])
    result = _clean_crm_prd_info(df)

    assert result.iloc[0]["prd_cost"] == 0

def test_product_line_mapping():
    df = make_prd_info_df(prd_line=["r"])
    result = _clean_crm_prd_info(df)

    assert result.iloc[0]["prd_line"] == "Road"

    df = make_prd_info_df(prd_line=["Z"])
    result = _clean_crm_prd_info(df)

    assert result.iloc[0]["prd_line"] == "n/a"

def test_prd_end_dt_calculated_from_next_version():
    df = pd.DataFrame({
        "prd_id": [1, 2],
        "prd_key": ["AC-HE-HL-U509", "AC-HE-HL-U509"],
        "prd_nm": ["A", "A"],
        "prd_cost": [25.0, 30.0],
        "prd_line": ["m", "m"],
        "prd_start_dt": ["2023-01-01", "2023-06-01"],
    })
    result = _clean_crm_prd_info(df)
    first_row = result[result["prd_start_dt"] == pd.Timestamp("2023-01-01")].iloc[0]

    assert first_row["prd_end_dt"] == pd.Timestamp("2023-05-31")

    last_row = result[result["prd_start_dt"] == pd.Timestamp("2023-06-01")].iloc[0]

    assert pd.isna(last_row["prd_end_dt"])
