import pandas as pd
from src.transform_customers import _clean_crm_cust_info, _clean_erp_cust_az12, _clean_erp_loc_a101

def make_cust_info_df(**overrides):
    base = {
        "cst_id": [1],
        "cst_key": ["AW001"],
        "cst_firstname": ["  John  "],
        "cst_lastname": ["Doe"],
        "cst_marital_status": ["s"],
        "cst_gndr": ["m"],
        "cst_create_date": ["2025-01-01"],
    }
    base.update(overrides)

    return pd.DataFrame(base)

def test_null_cst_id_is_dropped():
    df = make_cust_info_df(cst_id=[1, None], cst_key=["AW001", "AW002"],
                            cst_firstname=["John", "Jane"], cst_lastname=["Doe", "Smith"],
                            cst_marital_status=["s", "m"], cst_gndr=["m", "f"],
                            cst_create_date=["2025-01-01", "2025-01-02"])
    result = _clean_crm_cust_info(df)

    assert len(result) == 1
    assert result.iloc[0]["cst_id"] == 1

def test_duplicate_cst_id_keeps_most_recent():
    df = make_cust_info_df(
        cst_id=[1, 1],
        cst_key=["AW001", "AW001"],
        cst_firstname=["John", "John"],
        cst_lastname=["Doe", "Doe"],
        cst_marital_status=["s", "s"],
        cst_gndr=["m", "m"],
        cst_create_date=["2025-01-01", "2025-06-15"],
    )
    result = _clean_crm_cust_info(df)

    assert len(result) == 1
    assert result.iloc[0]["cst_create_date"] == pd.Timestamp("2025-06-15")

def test_marital_status_mapping():
    df = make_cust_info_df(cst_marital_status=["s"])
    result = _clean_crm_cust_info(df)

    assert result.iloc[0]["cst_marital_status"] == "Single"

    df = make_cust_info_df(cst_marital_status=["M"])
    result = _clean_crm_cust_info(df)

    assert result.iloc[0]["cst_marital_status"] == "Married"

    df = make_cust_info_df(cst_marital_status=["X"])
    result = _clean_crm_cust_info(df)

    assert result.iloc[0]["cst_marital_status"] == "n/a"

def test_gender_mapping():
    df = make_cust_info_df(cst_gndr=["f"])
    result = _clean_crm_cust_info(df)

    assert result.iloc[0]["cst_gndr"] == "Female"

def test_names_are_trimmed():
    df = make_cust_info_df(cst_firstname=["  John  "], cst_lastname=["  Doe  "])
    result = _clean_crm_cust_info(df)

    assert result.iloc[0]["cst_firstname"] == "John"
    assert result.iloc[0]["cst_lastname"] == "Doe"

def test_erp_cust_az12_strips_nas_prefix():
    df = pd.DataFrame({"cid": ["NASAW001", "AW002"], "bdate": ["1990-01-01", "1985-05-05"], "gen": ["M", "F"]})
    result = _clean_erp_cust_az12(df)

    assert result.iloc[0]["cid"] == "AW001"
    assert result.iloc[1]["cid"] == "AW002"

def test_erp_cust_az12_nulls_future_birthdate():
    df = pd.DataFrame({"cid": ["AW001"], "bdate": ["2999-01-01"], "gen": ["M"]})
    result = _clean_erp_cust_az12(df)

    assert pd.isna(result.iloc[0]["bdate"])

def test_erp_cust_az12_gender_mapping():
    df = pd.DataFrame({"cid": ["AW001", "AW002", "AW003"], "bdate": ["1990-01-01"] * 3, "gen": ["FEMALE", "male", "X"]})
    result = _clean_erp_cust_az12(df)

    assert list(result["gen"]) == ["Female", "Male", "n/a"]

def test_erp_loc_a101_country_standardization():
    df = pd.DataFrame({"cid": ["AW-001", "AW-002", "AW-003", "AW-004"], "cntry": ["DE", "US", "USA", ""]})
    result = _clean_erp_loc_a101(df)

    assert list(result["cntry"]) == ["Germany", "United States", "United States", "n/a"]
    assert list(result["cid"]) == ["AW001", "AW002", "AW003", "AW004"]
