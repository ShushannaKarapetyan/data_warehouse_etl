/*
=============================================================
Create Database and Tables: data_warehouse_etl
=============================================================
Script Purpose:
    Creates the 'data_warehouse_etl' database and its 3 warehouse tables
    (dim_customers, dim_products, fact_sales). All cleaning/
    transformation happens in pandas before loading, so this
    database holds only final, clean tables — no bronze/silver/
    gold layering needed here.

WARNING:
    Running this script will drop the 'data_warehouse_etl' database if it exists.
    All data in it will be permanently deleted. Proceed with caution
    and ensure you have proper backups before running this script.
=============================================================
*/

-- Drop and recreate the database
DROP DATABASE IF EXISTS data_warehouse_etl;
CREATE DATABASE data_warehouse_etl;
USE dwh;

-- Table: dim_customers
CREATE TABLE dim_customers (
    customer_key     INT AUTO_INCREMENT PRIMARY KEY,
    customer_id      INT,
    customer_number  VARCHAR(50),
    first_name       VARCHAR(50),
    last_name        VARCHAR(50),
    country          VARCHAR(50),
    marital_status   VARCHAR(20),
    gender           VARCHAR(20),
    birthdate        DATE,
    create_date      DATE
);

-- Table: dim_products
CREATE TABLE dim_products (
    product_key      INT AUTO_INCREMENT PRIMARY KEY,
    product_id       INT,
    product_number   VARCHAR(50),
    product_name     VARCHAR(100),
    category_id      VARCHAR(50),
    category         VARCHAR(50),
    subcategory      VARCHAR(50),
    maintenance      VARCHAR(20),
    cost             DECIMAL(10,2),
    product_line     VARCHAR(50),
    start_date       DATE
);

-- Table: fact_sales
CREATE TABLE fact_sales (
    order_number   VARCHAR(50),
    product_key    INT,
    customer_key   INT,
    order_date     DATE,
    shipping_date  DATE,
    due_date       DATE,
    sales          DECIMAL(12,2),
    quantity       INT,
    price          DECIMAL(10,2),
    FOREIGN KEY (product_key) REFERENCES dim_products(product_key),
    FOREIGN KEY (customer_key) REFERENCES dim_customers(customer_key)
);
