"""
Generate synthetic e-commerce data for analysis
Author: Undadi Nishank
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

# Configuration
NUM_CUSTOMERS = 5000
NUM_PRODUCTS = 200
START_DATE = datetime(2022, 1, 1)
END_DATE = datetime(2024, 11, 30)

print("Generating synthetic e-commerce data...")

# ==================== CUSTOMERS ====================
print("Creating customers...")

countries = ['USA', 'UK', 'Germany', 'France', 'Canada', 'Australia', 'India', 'Japan']
cities = {
    'USA': ['New York', 'Los Angeles', 'Chicago', 'Houston'],
    'UK': ['London', 'Manchester', 'Birmingham'],
    'Germany': ['Berlin', 'Munich', 'Hamburg'],
    'France': ['Paris', 'Lyon', 'Marseille'],
    'Canada': ['Toronto', 'Vancouver', 'Montreal'],
    'Australia': ['Sydney', 'Melbourne', 'Brisbane'],
    'India': ['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad'],
    'Japan': ['Tokyo', 'Osaka', 'Kyoto']
}

customers = []
for i in range(1, NUM_CUSTOMERS + 1):
    country = random.choice(countries)
    city = random.choice(cities[country])
    reg_date = START_DATE + timedelta(days=random.randint(0, (END_DATE - START_DATE).days))
    
    customers.append({
        'customer_id': i,
        'customer_name': f'Customer_{i}',
        'email': f'customer{i}@email.com',
        'country': country,
        'city': city,
        'registration_date': reg_date.strftime('%Y-%m-%d')
    })

df_customers = pd.DataFrame(customers)

# ==================== PRODUCTS ====================
print("Creating products...")

categories = {
    'Electronics': ['Laptop', 'Phone', 'Tablet', 'Headphones', 'Camera', 'Smartwatch'],
    'Clothing': ['Shirt', 'Pants', 'Dress', 'Jacket', 'Shoes', 'Hat'],
    'Home': ['Chair', 'Table', 'Lamp', 'Rug', 'Cushion', 'Mirror'],
    'Books': ['Fiction', 'Non-Fiction', 'Educational', 'Comics'],
    'Sports': ['Ball', 'Racket', 'Weights', 'Yoga Mat', 'Bicycle']
}

price_ranges = {
    'Electronics': (50, 1500),
    'Clothing': (20, 200),
    'Home': (30, 500),
    'Books': (10, 50),
    'Sports': (15, 300)
}

products = []
product_id = 1
for category, subcategories in categories.items():
    for sub in subcategories:
        for i in range(1, 8):
            price_min, price_max = price_ranges[category]
            products.append({
                'product_id': product_id,
                'product_name': f'{sub} Model {i}',
                'category': category,
                'sub_category': sub,
                'unit_price': round(random.uniform(price_min, price_max), 2)
            })
            product_id += 1

df_products = pd.DataFrame(products)

# ==================== ORDERS & ORDER ITEMS ====================
print("Creating orders and order items...")

orders = []
order_items = []
order_id = 1
order_item_id = 1

# Create orders for each customer with varying behavior
for cust_id in range(1, NUM_CUSTOMERS + 1):
    cust_reg = df_customers[df_customers['customer_id'] == cust_id]['registration_date'].values[0]
    cust_reg_date = datetime.strptime(cust_reg, '%Y-%m-%d')
    
    # Determine customer behavior (some buy more, some less)
    behavior_type = random.choices(
        ['champion', 'loyal', 'occasional', 'one_time'],
        weights=[0.15, 0.25, 0.35, 0.25]
    )[0]
    
    if behavior_type == 'champion':
        num_orders = random.randint(8, 20)
    elif behavior_type == 'loyal':
        num_orders = random.randint(4, 8)
    elif behavior_type == 'occasional':
        num_orders = random.randint(2, 4)
    else:
        num_orders = 1
    
    # Create orders for this customer
    last_order_date = cust_reg_date
    for order_num in range(num_orders):
        # Calculate order date
        if order_num == 0:
            order_date = cust_reg_date + timedelta(days=random.randint(0, 7))
        else:
            days_gap = random.randint(7, 90)
            order_date = last_order_date + timedelta(days=days_gap)
        
        if order_date > END_DATE:
            break
        
        last_order_date = order_date
        ship_date = order_date + timedelta(days=random.randint(1, 5))
        
        # Randomly select products for this order
        num_items = random.randint(1, 5)
        order_products = random.sample(range(1, len(df_products) + 1), num_items)
        
        order_total = 0
        for prod_id in order_products:
            product = df_products[df_products['product_id'] == prod_id].iloc[0]
            quantity = random.randint(1, 3)
            discount = random.choice([0, 0, 0, 0.05, 0.10, 0.15])
            line_total = product['unit_price'] * quantity * (1 - discount)
            order_total += line_total
            
            order_items.append({
                'order_item_id': order_item_id,
                'order_id': order_id,
                'product_id': prod_id,
                'quantity': quantity,
                'unit_price': product['unit_price'],
                'discount': discount,
                'line_total': round(line_total, 2)
            })
            order_item_id += 1
        
        orders.append({
            'order_id': order_id,
            'customer_id': cust_id,
            'order_date': order_date.strftime('%Y-%m-%d'),
            'ship_date': ship_date.strftime('%Y-%m-%d'),
            'total_amount': round(order_total, 2),
            'order_status': 'Completed'
        })
        order_id += 1
    
    if cust_id % 500 == 0:
        print(f"  Processed {cust_id}/{NUM_CUSTOMERS} customers...")

df_orders = pd.DataFrame(orders)
df_order_items = pd.DataFrame(order_items)

# ==================== SAVE TO CSV ====================
print("\nSaving data to CSV files...")

df_customers.to_csv('data/raw/customers.csv', index=False)
df_products.to_csv('data/raw/products.csv', index=False)
df_orders.to_csv('data/raw/orders.csv', index=False)
df_order_items.to_csv('data/raw/order_items.csv', index=False)

print("\nData generation complete!")
print(f"Customers: {len(df_customers)}")
print(f"Products: {len(df_products)}")
print(f"Orders: {len(df_orders)}")
print(f"Order Items: {len(df_order_items)}")
print(f"\nTotal Revenue: ${df_orders['total_amount'].sum():,.2f}")
print(f"Date Range: {df_orders['order_date'].min()} to {df_orders['order_date'].max()}")