-- E-Commerce Analytics Queries
-- Author: Undadi Nishank

USE ecommerce_db;

-- ================================================
-- 1. RFM ANALYSIS
-- ================================================

-- Calculate RFM scores for all customers
INSERT INTO rfm_scores (customer_id, recency, frequency, monetary, r_score, f_score, m_score, rfm_segment)
WITH rfm_calc AS (
    SELECT 
        c.customer_id,
        DATEDIFF(CURDATE(), MAX(o.order_date)) as recency,
        COUNT(DISTINCT o.order_id) as frequency,
        SUM(o.total_amount) as monetary
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id
    WHERE o.order_status = 'Completed'
    GROUP BY c.customer_id
),
rfm_scores_calc AS (
    SELECT 
        customer_id,
        recency,
        frequency,
        monetary,
        NTILE(5) OVER (ORDER BY recency DESC) as r_score,
        NTILE(5) OVER (ORDER BY frequency ASC) as f_score,
        NTILE(5) OVER (ORDER BY monetary ASC) as m_score
    FROM rfm_calc
)
SELECT 
    customer_id,
    recency,
    frequency,
    monetary,
    r_score,
    f_score,
    m_score,
    CASE 
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
        WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'Loyal'
        WHEN r_score >= 3 AND f_score <= 2 THEN 'Potential Loyalist'
        WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
        WHEN r_score <= 2 AND f_score <= 2 AND m_score >= 3 THEN 'Cant Lose'
        WHEN r_score <= 2 AND f_score <= 2 THEN 'Lost'
        ELSE 'Others'
    END as rfm_segment
FROM rfm_scores_calc;

-- View RFM segment distribution
SELECT 
    rfm_segment,
    COUNT(*) as customer_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage,
    ROUND(AVG(monetary), 2) as avg_revenue,
    ROUND(SUM(monetary), 2) as total_revenue
FROM rfm_scores
GROUP BY rfm_segment
ORDER BY total_revenue DESC;

-- ================================================
-- 2. COHORT ANALYSIS
-- ================================================

-- Create cohort data
INSERT INTO customer_cohorts (customer_id, cohort_month, order_month, cohort_index)
WITH first_purchase AS (
    SELECT 
        customer_id,
        DATE_FORMAT(MIN(order_date), '%Y-%m-01') as cohort_month
    FROM orders
    WHERE order_status = 'Completed'
    GROUP BY customer_id
)
SELECT 
    o.customer_id,
    fp.cohort_month,
    DATE_FORMAT(o.order_date, '%Y-%m-01') as order_month,
    PERIOD_DIFF(
        DATE_FORMAT(o.order_date, '%Y%m'),
        DATE_FORMAT(fp.cohort_month, '%Y%m')
    ) as cohort_index
FROM orders o
JOIN first_purchase fp ON o.customer_id = fp.customer_id
WHERE o.order_status = 'Completed';

-- Calculate retention rates by cohort
SELECT 
    cohort_month,
    COUNT(DISTINCT CASE WHEN cohort_index = 0 THEN customer_id END) as month_0,
    COUNT(DISTINCT CASE WHEN cohort_index = 1 THEN customer_id END) as month_1,
    COUNT(DISTINCT CASE WHEN cohort_index = 2 THEN customer_id END) as month_2,
    COUNT(DISTINCT CASE WHEN cohort_index = 3 THEN customer_id END) as month_3,
    COUNT(DISTINCT CASE WHEN cohort_index = 4 THEN customer_id END) as month_4,
    COUNT(DISTINCT CASE WHEN cohort_index = 5 THEN customer_id END) as month_5,
    COUNT(DISTINCT CASE WHEN cohort_index = 6 THEN customer_id END) as month_6
FROM customer_cohorts
GROUP BY cohort_month
ORDER BY cohort_month;

-- ================================================
-- 3. CUSTOMER METRICS
-- ================================================

-- Customer Lifetime Value (CLV)
SELECT 
    customer_id,
    customer_name,
    total_revenue as clv,
    total_orders,
    ROUND(total_revenue / total_orders, 2) as avg_order_value,
    days_since_last_order,
    CASE 
        WHEN days_since_last_order <= 30 THEN 'Active'
        WHEN days_since_last_order <= 90 THEN 'At Risk'
        ELSE 'Churned'
    END as customer_status
FROM customer_summary
ORDER BY clv DESC
LIMIT 100;

-- Customer Acquisition by Month
SELECT 
    DATE_FORMAT(registration_date, '%Y-%m') as month,
    COUNT(*) as new_customers,
    SUM(COUNT(*)) OVER (ORDER BY DATE_FORMAT(registration_date, '%Y-%m')) as cumulative_customers
FROM customers
GROUP BY DATE_FORMAT(registration_date, '%Y-%m')
ORDER BY month;

-- Repeat Purchase Rate
SELECT 
    COUNT(CASE WHEN total_orders > 1 THEN 1 END) * 100.0 / COUNT(*) as repeat_purchase_rate,
    AVG(total_orders) as avg_orders_per_customer
FROM customer_summary;

-- ================================================
-- 4. PRODUCT ANALYSIS
-- ================================================

-- Top selling products
SELECT 
    p.product_name,
    p.category,
    COUNT(DISTINCT oi.order_id) as order_count,
    SUM(oi.quantity) as units_sold,
    ROUND(SUM(oi.line_total), 2) as total_revenue,
    ROUND(AVG(oi.line_total), 2) as avg_revenue_per_order
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_status = 'Completed'
GROUP BY p.product_id, p.product_name, p.category
ORDER BY total_revenue DESC
LIMIT 20;

-- Category performance
SELECT 
    p.category,
    COUNT(DISTINCT o.order_id) as order_count,
    COUNT(DISTINCT o.customer_id) as unique_customers,
    SUM(oi.quantity) as units_sold,
    ROUND(SUM(oi.line_total), 2) as revenue,
    ROUND(AVG(oi.line_total), 2) as avg_basket_value
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_status = 'Completed'
GROUP BY p.category
ORDER BY revenue DESC;

-- Product affinity (products bought together)
SELECT 
    p1.product_name as product_1,
    p2.product_name as product_2,
    COUNT(*) as times_bought_together
FROM order_items oi1
JOIN order_items oi2 ON oi1.order_id = oi2.order_id AND oi1.product_id < oi2.product_id
JOIN products p1 ON oi1.product_id = p1.product_id
JOIN products p2 ON oi2.product_id = p2.product_id
GROUP BY p1.product_id, p2.product_id, p1.product_name, p2.product_name
HAVING COUNT(*) >= 10
ORDER BY times_bought_together DESC
LIMIT 20;

-- ================================================
-- 5. REVENUE ANALYSIS
-- ================================================

-- Monthly revenue trends with growth rate
WITH monthly_data AS (
    SELECT 
        DATE_FORMAT(order_date, '%Y-%m') as month,
        SUM(total_amount) as revenue
    FROM orders
    WHERE order_status = 'Completed'
    GROUP BY DATE_FORMAT(order_date, '%Y-%m')
)
SELECT 
    month,
    revenue,
    LAG(revenue) OVER (ORDER BY month) as prev_month_revenue,
    ROUND(
        (revenue - LAG(revenue) OVER (ORDER BY month)) * 100.0 / 
        LAG(revenue) OVER (ORDER BY month), 
    2) as growth_rate_pct
FROM monthly_data
ORDER BY month;

-- Revenue by country
SELECT 
    c.country,
    COUNT(DISTINCT o.customer_id) as customers,
    COUNT(DISTINCT o.order_id) as orders,
    ROUND(SUM(o.total_amount), 2) as revenue,
    ROUND(AVG(o.total_amount), 2) as avg_order_value
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_status = 'Completed'
GROUP BY c.country
ORDER BY revenue DESC;

-- Day of week performance
SELECT 
    DAYNAME(order_date) as day_of_week,
    COUNT(*) as order_count,
    ROUND(SUM(total_amount), 2) as revenue,
    ROUND(AVG(total_amount), 2) as avg_order_value
FROM orders
WHERE order_status = 'Completed'
GROUP BY DAYNAME(order_date), DAYOFWEEK(order_date)
ORDER BY DAYOFWEEK(order_date);

-- ================================================
-- 6. CHURN ANALYSIS
-- ================================================

-- Churned customers (no purchase in last 90 days)
SELECT 
    c.customer_id,
    c.customer_name,
    c.email,
    cs.total_revenue,
    cs.total_orders,
    cs.last_order_date,
    cs.days_since_last_order
FROM customers c
JOIN customer_summary cs ON c.customer_id = cs.customer_id
WHERE cs.days_since_last_order > 90
ORDER BY cs.total_revenue DESC;

-- Churn rate calculation
SELECT 
    ROUND(
        COUNT(CASE WHEN days_since_last_order > 90 THEN 1 END) * 100.0 / COUNT(*),
    2) as churn_rate_pct,
    COUNT(CASE WHEN days_since_last_order > 90 THEN 1 END) as churned_customers,
    COUNT(*) as total_customers
FROM customer_summary;