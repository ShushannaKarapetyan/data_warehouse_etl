# Data Warehouse ETL Project
This project demonstrates a data warehousing solution built with **Python, pandas, and MySQL**, using an **ETL (Extract, Transform, Load)** architecture.

## 🏗️ Data Architecture

This project uses a **Staging → Data Warehouse** architecture — the classic ETL pattern where transformation happens *before* data is loaded, not inside the database:

- **Extract**: Source CSV files (CRM and ERP systems) are read into pandas DataFrames.
- **Transform**: All cleaning, standardization, deduplication, and business-key resolution happens **in memory, in pandas**.
- **Load**: Only clean, business-ready data is written into the MySQL warehouse, directly into three final star-schema tables: `dim_customers`, `dim_products` and `fact_sales`.

## 📖 Project Overview

This project involves:
1. **Data Architecture**: Designing a Staging → Warehouse pipeline using Python as the transformation engine and MySQL as the destination.
2. **ETL Pipeline**: Extracting CSV source data, transforming it with pandas, validating it, and loading it into a MySQL star schema.
3. **Data Modeling**: Building `dim_customers`, `dim_products` and `fact_sales` tables with surrogate keys and enforced foreign key relationships.
4. **Testing**: Unit tests (pytest) covering the core transformation logic for each table.
5. **Logging**: Centralized logging to file and console

---

## 🚀 Project Requirements

### Building the Data Warehouse (ETL Pipeline)

#### Specifications
- **Data Sources**: Import data from two source systems (ERP and CRM), provided as CSV files.
- **Data Quality**: Cleanse and resolve data quality issues (missing IDs, inconsistent codes, invalid dates, mismatched sales figures) before data ever reaches the warehouse.
- **Integration**: Combine both sources into a single, user-friendly star schema designed for analytical queries.
- **Scope**: Focus on the latest dataset only; historization of data (SCD) is not required.
- **Documentation**: Provide clear documentation of the data model and pipeline to support both business stakeholders and analytics teams.

---

## 📂 Repository Structure

```
data-warehouse-etl/
│
├── datasets/                       # Raw source CSV files (CRM and ERP data)
│   ├── source_crm/
│   └── source_erp/
│
├── docs/                            # Project documentation and architecture diagrams
│   ├── data_model.drawio            # Star schema diagram (dim_customers, dim_products, fact_sales)
│   └── data_flow.drawio             # Source -> pipeline -> warehouse data lineage diagram
│
├── sql/
│   └── ddl.sql                       # One-time schema setup: creates the database and its 3 tables
│
├── src/                              # Core ETL pipeline modules
│   ├── __init__.py
│   ├── db_connection.py             # SQLAlchemy engine setup
│   ├── extract.py                   # Reads and normalizes the source CSVs into DataFrames
│   ├── transform_customers.py       # Cleans and joins source data into dim_customers
│   ├── transform_products.py        # Cleans and joins source data into dim_products
│   ├── transform_sales.py           # Cleans sales data and resolves surrogate keys into fact_sales
│   └── load.py                      # Truncates and loads each DataFrame into MySQL
│
├── scripts/
│   └── main.py                      # Orchestrates the full pipeline
│
├── tests/                           # Unit tests for each transform module (pytest)
│   ├── test_transform_customers.py
│   ├── test_transform_products.py
│   └── test_transform_sales.py
│
├── docs/                               # Project documentation and architecture details
│   ├── ETL_mindmap.jpg                 # JPG image file shows all different techniquies and methods of ETL
│   ├── data_catalog.md                 # Catalog of datasets, including field descriptions and metadata
│   ├── data_flow.drawio                # Draw.io file for the data flow diagram
│   ├── data_flow.jpg
│   ├── data_model.drawio               # Draw.io file for data models (star schema)
│   ├── data_model.jpg
│
├── .env.example                      # Template for required environment variables
├── .gitignore
├── pyproject.toml                    # Project metadata, dependencies, and pytest configuration
├── requirements.txt
└── README.md
```

---

## How the Pipeline Works

1. **`sql/ddl/init_database.sql`** is run once, manually, to create the `data_warehouse_etl` database and its 3 tables (`dim_customers`, `dim_products`, `fact_sales`) with proper data types and foreign key constraints.
2. **`scripts/main.py`** is run to execute the pipeline:
   - Connects to MySQL using credentials loaded from `.env`
   - Extracts source CSVs into pandas DataFrames
   - Transforms and joins the CRM/ERP sources into the 3 warehouse tables
   - Truncates and loads each table into MySQL, in dependency order (dimensions tables first, then fact table)
3. Every run is logged to both the console and in the log file, with timestamps and duration.

---

## 🛠️ Commands

```bash
# 1. Run the pipeline
python scripts/main.py

# 2. Run unit tests
pytest tests/ -v
```

---

## 🧰 Tech Stack

- **Python** — pipeline logic and orchestration
- **pandas** — extraction, cleaning, and transformation
- **SQLAlchemy** — database connectivity
- **MySQL** — data warehouse storage
- **pytest** — unit testing
- **python-dotenv** — environment-based configuration

---
