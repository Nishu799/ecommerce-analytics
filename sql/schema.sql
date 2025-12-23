-- E-Commerce Analytics Database Schema
-- Author: Undadi Nishank
-- Date: December 2024

DROP DATABASE IF EXISTS ecommerce_db;
CREATE DATABASE ecommerce_db;
USE ecommerce_db;

-- Customers Table
CREATE TABLE customers (
    customer_id INT PRIMARY KEY,
    customer_name VARCHAR(100),
    email VARCHAR(100),
    country VARCHAR(50),
    city VARCHAR(50),
    registration_date DATE,
    customer_segment VARCHAR(20)
);

-- Products Table
CREATE TABLE products (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(200),
    category VARCHAR(50),
    sub_category VARCHAR(50),
    unit_price DECIMAL(10,2)
);

-- Orders Table
CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    customer_id INT,
    order_date DATE,
    ship_date DATE,
    total_amount DECIMAL(10,2),
    order_status VARCHAR(20),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Order Items Table
CREATE TABLE order_items (
    order_item_id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT,
    product_id INT,
    quantity INT,
    unit_price DECIMAL(10,2),
    discount DECIMAL(5,2),
    line_total DECIMAL(10,2),
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- RFM Scores Table (for analysis results)
CREATE TABLE rfm_scores (
    customer_id INT PRIMARY KEY,
    recency INT,
    frequency INT,
    monetary DECIMAL(10,2),
    r_score INT,
    f_score INT,
    m_score INT,
    rfm_segment VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Customer Cohorts Table
CREATE TABLE customer_cohorts (
    customer_id INT,
    cohort_month DATE,
    order_month DATE,
    cohort_index INT,
    PRIMARY KEY (customer_id, order_month),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Indexes for performance
CREATE INDEX idx_customer_id ON orders(customer_id);
CREATE INDEX idx_order_date ON orders(order_date);
CREATE INDEX idx_product_id ON order_items(product_id);
CREATE INDEX idx_order_id ON order_items(order_id);
CREATE INDEX idx_registration_date ON customers(registration_date);

-- Views for common queries
CREATE VIEW customer_summary AS
SELECT 
    c.customer_id,
    c.customer_name,
    c.country,
    COUNT(DISTINCT o.order_id) as total_orders,
    SUM(o.total_amount) as total_revenue,
    AVG(o.total_amount) as avg_order_value,
    MIN(o.order_date) as first_order_date,
    MAX(o.order_date) as last_order_date,
    DATEDIFF(CURDATE(), MAX(o.order_date)) as days_since_last_order
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.customer_name, c.country;

CREATE VIEW monthly_revenue AS
SELECT 
    DATE_FORMAT(order_date, '%Y-%m') as month,
    COUNT(DISTINCT order_id) as total_orders,
    COUNT(DISTINCT customer_id) as unique_customers,
    SUM(total_amount) as revenue,
    AVG(total_amount) as avg_order_value
FROM orders
WHERE order_status = 'Completed'
GROUP BY DATE_FORMAT(order_date, '%Y-%m')
ORDER BY month;