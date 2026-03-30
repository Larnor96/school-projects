-- 1. TIME-BASED ANALYSIS: Monthly Sales Trend

/* This query calculates monthly sales performance by summing total sales and counting unique orders for each year and month, 
using the date dimension to group and order the results chronologically.
*/

-- Selects year, month, and month name from the date dimension
SELECT 
    dd.year,
    dd.month,
    dd.month_name,

    -- Calculates total sales amount for each month
    SUM(foi.total_price) AS total_sales,

    -- Counts unique orders to show order volume per month
    COUNT(DISTINCT foi.order_id) AS total_orders

-- Fact table with sales values
FROM dwh.fact_order_items foi

-- Join to date dimension to access year and month info
JOIN dwh.dim_date dd ON foi.date_key = dd.date_key

-- Group by year and month to aggregate monthly totals
GROUP BY dd.year, dd.month, dd.month_name

-- Sort chronologically by year and month
ORDER BY dd.year, dd.month;



---------------------------------------------------------------------------

-- 2. Aggregation Operations: 

/* This query shows total sales by customer state and product category, 
including subtotals per state and an overall total, 
using the SQL ROLLUP operator for multi-level aggregation.*/

-- Selects customer state and product category for multi level totals
SELECT 
    dc.customer_state,
    dp.product_category_name,

    -- Calculates total sales for each combination of state and category
    SUM(foi.total_price) AS total_sales

-- Fact table containing order item data
FROM dwh.fact_order_items foi

-- Join to customer dimension to group by state
JOIN dwh.dim_customer dc ON foi.customer_key = dc.customer_key

-- Join to product dimension to group by product category
JOIN dwh.dim_product dp ON foi.product_key = dp.product_key

-- Adds subtotals per state and a grand total using ROLLUP
GROUP BY ROLLUP (dc.customer_state, dp.product_category_name)

-- Orders results by state and descending sales
ORDER BY dc.customer_state, total_sales DESC;


---------------------------------------------------------------------------

-- 3. WINDOW FUNCTION: Rank Top Product Categories by Revenue

/* This query ranks product categories by total revenue using a window function (RANK()), 
showing the top 10 best-performing categories. */

-- Selects product categories and total revenue
SELECT 
    dp.product_category_name,

    -- Calculates total revenue per category
    SUM(foi.total_price) AS total_revenue,

    -- Assigns a rank based on total revenue (highest = rank 1)
    RANK() OVER (ORDER BY SUM(foi.total_price) DESC) AS revenue_rank

-- Fact table with order item data
FROM dwh.fact_order_items foi

-- Join to product dimension to group by category
JOIN dwh.dim_product dp ON foi.product_key = dp.product_key

-- Groups data by product category for aggregation
GROUP BY dp.product_category_name

-- Orders results by rank (highest revenue first)
ORDER BY revenue_rank
LIMIT 10;


---------------------------------------------------------------------------

-- 4. COMPLEX FILTERING: High-Value Orders with Good Reviews

/*This query filters orders to show only high value purchases with positive reviews,
 combining data from both the sales and delivery fact tables. */

-- Selects order details, customer state, category, review score, and total price
SELECT 
    fd.order_id,
    dc.customer_state,
    dp.product_category_name,
    fd.review_score,
    foi.total_price

-- Combines delivery and order item data
FROM dwh.fact_delivery fd
JOIN dwh.fact_order_items foi ON fd.order_id = foi.order_id

-- Joins to customer and product dimensions for extra context
JOIN dwh.dim_customer dc ON fd.customer_key = dc.customer_key
JOIN dwh.dim_product dp ON foi.product_key = dp.product_key

-- Filters to show only well-rated (review_score >= 4)
-- and above-average value orders (using a subquery)
WHERE fd.review_score >= 4
  AND foi.total_price > (
        SELECT AVG(total_price) 
        FROM dwh.fact_order_items
    )

-- Sorts highest-value orders first
ORDER BY foi.total_price DESC;

---------------------------------------------------------------------------------

-- 5. BUSINESS METRIC 1: Average Order Value by State

/* This query calculates the average order value for each customer state by dividing total sales by the number of unique orders, 
helping identify regions with higher spending per order.*/

-- Selects each customer state
SELECT 
    dc.customer_state,

    -- Calculates average order value (total sales / number of unique orders)
    SUM(foi.total_price) / COUNT(DISTINCT foi.order_id) AS avg_order_value

-- Uses fact table for total sales data
FROM dwh.fact_order_items foi

-- Join to customer dimension to group by state
JOIN dwh.dim_customer dc ON foi.customer_key = dc.customer_key

-- Groups results per state
GROUP BY dc.customer_state

-- Orders states from highest to lowest average order value
ORDER BY avg_order_value DESC;

--------------------------------------------------------------------------------

-- 6. BUSINESS METRIC 2: On-Time Delivery Rate by State

/*This query calculates the on time delivery rate per state, 
showing how efficiently each region handles deliveries by comparing on time vs total deliveries. */

-- Selects each customer state and counts delivery performance
SELECT 
    dc.customer_state,

    -- Counts all deliveries made to that state
    COUNT(*) AS total_deliveries,

    -- Counts deliveries that were not marked as late
    SUM(CASE WHEN fd.is_late = FALSE THEN 1 ELSE 0 END) AS on_time_deliveries,

    -- Calculates percentage of on-time deliveries
    ROUND(SUM(CASE WHEN fd.is_late = FALSE THEN 1 ELSE 0 END)::numeric / COUNT(*) * 100, 2) AS on_time_rate

-- Uses the delivery fact table
FROM dwh.fact_delivery fd

-- Joins to customer dimension to group by state
JOIN dwh.dim_customer dc ON fd.customer_key = dc.customer_key

-- Groups results per customer state
GROUP BY dc.customer_state

-- Orders states by highest on-time delivery rate
ORDER BY on_time_rate DESC;
