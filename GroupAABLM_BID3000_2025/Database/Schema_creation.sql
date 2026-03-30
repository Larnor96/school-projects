-- =============================================================
-- SCHEMA: dwh
-- Purpose: Store cleaned, structured data ready for BI analysis
-- =============================================================
 
CREATE SCHEMA IF NOT EXISTS dwh;
 
------------------------------------------------------------
-- 1. Dimension: Customer
------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dwh.dim_customer (
    customer_key SERIAL PRIMARY KEY,
    customer_id TEXT,          
    customer_unique_id TEXT,   
    customer_city TEXT,
    customer_state TEXT
);
 
------------------------------------------------------------
-- 2. Dimension: Seller
------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dwh.dim_seller (
    seller_key SERIAL PRIMARY KEY,
    seller_id TEXT,
    seller_city TEXT,
    seller_state TEXT
);
 
------------------------------------------------------------
-- 3. Dimension: Product
------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dwh.dim_product (
    product_key SERIAL PRIMARY KEY,
    product_id TEXT,
    product_category_name TEXT
);
 
------------------------------------------------------------
-- 4. Dimension: Date
------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dwh.dim_date (
    date_key SERIAL PRIMARY KEY,
    full_date DATE,
    year INT,
    month INT,
    day INT,
    month_name TEXT,
    weekday TEXT
);
 
------------------------------------------------------------
-- 5. Fact Table: Order Items (Sales)
------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dwh.fact_order_items
(
    order_id text COLLATE pg_catalog."default",
    customer_key integer,
    seller_key integer,
    product_key integer,
    date_key integer,
    order_item_id integer,
    item_price numeric,
    freight_price numeric,
    total_price numeric,
    CONSTRAINT fk_customer FOREIGN KEY (customer_key)
        REFERENCES dwh.dim_customer (customer_key) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT fk_date FOREIGN KEY (date_key)
        REFERENCES dwh.dim_date (date_key) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT fk_product FOREIGN KEY (product_key)
        REFERENCES dwh.dim_product (product_key) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT fk_seller FOREIGN KEY (seller_key)
        REFERENCES dwh.dim_seller (seller_key) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
);

 
------------------------------------------------------------
-- 6. Fact Table: Delivery / Review
------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dwh.fact_delivery (
    order_id TEXT,
    customer_key INT,
    date_key_purchase INT,
    date_key_estimated INT,
    date_key_delivered INT,
    delivery_time_days NUMERIC,
    is_late BOOLEAN,
    review_score INT,
    review_comment_message TEXT,
    CONSTRAINT fk_customer_delivery FOREIGN KEY (customer_key) REFERENCES dwh.dim_customer(customer_key),
    CONSTRAINT fk_date_p FOREIGN KEY (date_key_purchase) REFERENCES dwh.dim_date(date_key),
    CONSTRAINT fk_date_e FOREIGN KEY (date_key_estimated) REFERENCES dwh.dim_date(date_key),
    CONSTRAINT fk_date_d FOREIGN KEY (date_key_delivered) REFERENCES dwh.dim_date(date_key)
);

------------------------------------------------------------
-- 7. Indexes
------------------------------------------------------------
CREATE INDEX idx_customer_unique_id ON dwh.dim_customer (customer_unique_id);
CREATE INDEX idx_date_full_date ON dwh.dim_date (full_date);
CREATE INDEX idx_product_id ON dwh.dim_product (product_id);
CREATE INDEX idx_seller_id ON dwh.dim_seller (seller_id);

CREATE INDEX idx_foi_customer_key ON dwh.fact_order_items (customer_key);
CREATE INDEX idx_foi_seller_key ON dwh.fact_order_items (seller_key);
CREATE INDEX idx_foi_product_key ON dwh.fact_order_items (product_key);
CREATE INDEX idx_foi_date_key ON dwh.fact_order_items (date_key);
CREATE INDEX idx_foi_order_id ON dwh.fact_order_items (order_id);

CREATE INDEX idx_fd_customer_key ON dwh.fact_delivery (customer_key);
CREATE INDEX idx_fd_seller_key ON dwh.fact_delivery (seller_key);
CREATE INDEX idx_fd_order_id ON dwh.fact_delivery (order_id);
CREATE INDEX idx_fd_date_purchase ON dwh.fact_delivery (date_key_purchase);
CREATE INDEX idx_fd_date_estimated ON dwh.fact_delivery (date_key_estimated);
CREATE INDEX idx_fd_date_delivered ON dwh.fact_delivery (date_key_delivered);