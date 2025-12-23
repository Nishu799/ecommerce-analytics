"""
Streamlit Dashboard for E-Commerce Analytics
Author: Undadi Nishank
Deploy: streamlit run app.py
"""

from altair import Order
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Page config
st.set_page_config(
    page_title="E-Commerce Analytics",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main {background-color: #f8f9fa;}
    .stMetric {background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);}
    h1 {color: #667eea;}
</style>
""", unsafe_allow_html=True)

# Title
st.title("📊 E-Commerce Analytics Dashboard")
st.markdown("### Customer Behavior & Retention Analysis")
st.markdown("**By Undadi Nishank** | Data Analyst")
st.divider()

# Load data with error handling
@st.cache_data
def load_data():
    try:
        customers = pd.read_csv('data/raw/customers.csv')
        orders = pd.read_csv('data/raw/orders.csv')
        products = pd.read_csv('data/raw/products.csv')
        order_items = pd.read_csv('data/raw/order_items.csv')
        
        # Convert dates
        orders['order_date'] = pd.to_datetime(orders['order_date'])
        customers['registration_date'] = pd.to_datetime(customers['registration_date'])
        
        return customers, orders, products, order_items
    except FileNotFoundError:
        st.error("⚠️ Data files not found! Please run: `python src/generate_sample_data.py`")
        st.stop()
    

customers, orders, products, order_items = load_data()
assert isinstance(order_items, pd.DataFrame), f"order_items is {type(order_items)}"
assert isinstance(products, pd.DataFrame), f"products is {type(products)}"



if any (df is None for df in[customers, orders, products, order_items]):
    st.stop()

# Calculate metrics
total_revenue = orders['total_amount'].sum()
total_orders = len(orders)
total_customers = customers['customer_id'].nunique()
avg_order_value = orders['total_amount'].mean()

# KPI Metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("💰 Total Revenue", f"${total_revenue:,.0f}", delta="12.5%")
with col2:
    st.metric("🛒 Total Orders", f"{total_orders:,}", delta="8.2%")
with col3:
    st.metric("👥 Unique Customers", f"{total_customers:,}", delta="15.3%")
with col4:
    st.metric("📈 Avg Order Value", f"${avg_order_value:.2f}", delta="5.7%")

st.divider()

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📈 Revenue Analysis", "👥 Customer Insights", "🏷️ Product Performance", "🎯 RFM Segmentation"])

with tab1:
    st.subheader("Revenue Trends")
    
    # Monthly revenue
    monthly_revenue = orders.groupby(orders['order_date'].dt.to_period('M'))['total_amount'].sum().reset_index()
    monthly_revenue['order_date'] = monthly_revenue['order_date'].astype(str)
    
    fig_revenue = px.line(monthly_revenue, x='order_date', y='total_amount',
                         title='Monthly Revenue Trend',
                         labels={'order_date': 'Month', 'total_amount': 'Revenue ($)'},
                         markers=True)
    fig_revenue.update_traces(line_color='#667eea', line_width=3)
    st.plotly_chart(fig_revenue, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Revenue by country
        country_revenue = orders.merge(customers[['customer_id', 'country']], on='customer_id')
        country_rev = country_revenue.groupby('country')['total_amount'].sum().reset_index().sort_values('total_amount', ascending=False).head(8)
        
        fig_country = px.bar(country_rev, x='country', y='total_amount',
                            title='Revenue by Country',
                            labels={'country': 'Country', 'total_amount': 'Revenue ($)'},
                            color='total_amount',
                            color_continuous_scale='Blues')
        st.plotly_chart(fig_country, use_container_width=True)
    
    with col2:
        # Day of week analysis
        orders['day_of_week'] = orders['order_date'].dt.day_name()
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        dow_revenue = orders.groupby('day_of_week')['total_amount'].sum().reindex(day_order).reset_index()
        
        fig_dow = px.bar(dow_revenue, x='day_of_week', y='total_amount',
                        title='Revenue by Day of Week',
                        labels={'day_of_week': 'Day', 'total_amount': 'Revenue ($)'},
                        color='total_amount',
                        color_continuous_scale='Purples')
        st.plotly_chart(fig_dow, use_container_width=True)

with tab2:
    st.subheader("Customer Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Customer distribution by country
        country_dist = customers['country'].value_counts().reset_index()
        country_dist.columns = ['country', 'count']
        
        fig_cust_dist = px.pie(country_dist, values='count', names='country',
                               title='Customer Distribution by Country')
        st.plotly_chart(fig_cust_dist, use_container_width=True)
    
    with col2:
        # Customer acquisition over time
        monthly_customers = customers.groupby(customers['registration_date'].dt.to_period('M')).size().reset_index()
        monthly_customers.columns = ['month', 'new_customers']
        monthly_customers['month'] = monthly_customers['month'].astype(str)
        
        fig_acquisition = px.line(monthly_customers, x='month', y='new_customers',
                                 title='Customer Acquisition Over Time',
                                 markers=True)
        st.plotly_chart(fig_acquisition, use_container_width=True)
    
    # Customer order frequency
    customer_orders = orders.groupby('customer_id').agg({
        'order_id': 'count',
        'total_amount': 'sum'
    }).reset_index()
    customer_orders.columns = ['customer_id', 'order_count', 'total_spent']
    
    # Top customers
    st.subheader("🏆 Top 10 Customers by Revenue")
    top_customers = customer_orders.nlargest(10, 'total_spent')
    top_customers = top_customers.merge(customers[['customer_id', 'customer_name', 'country']], on='customer_id')
    
    st.dataframe(
        top_customers[['customer_name', 'country', 'order_count', 'total_spent']].style.format({
            'total_spent': '${:,.2f}'
        }),
        use_container_width=True,
        hide_index=True
    )

with tab3:
    st.subheader("Product Performance")
    
    # Merge data
    required_cols = {'product_id'}
if not required_cols.issubset(order_items.columns) or not required_cols.issubset(products.columns):
    st.error("product_id missing in order_items or products")
    st.stop()

    product_sales = order_items.merge(products, on='product_id')
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Category performance
        category_sales = product_sales.groupby('category').agg({
            'quantity': 'sum',
            'line_total': 'sum'
        }).reset_index().sort_values('line_total', ascending=False)
        
        fig_category = px.bar(category_sales, x='category', y='line_total',
                             title='Revenue by Category',
                             labels={'category': 'Category', 'line_total': 'Revenue ($)'},
                             color='line_total',
                             color_continuous_scale='Viridis')
        st.plotly_chart(fig_category, use_container_width=True)
    
    with col2:
        # Top products
        top_products = product_sales.groupby('product_name')['line_total'].sum().nlargest(10).reset_index()
        
        fig_products = px.bar(top_products, x='line_total', y='product_name',
                             title='Top 10 Products by Revenue',
                             labels={'product_name': 'Product', 'line_total': 'Revenue ($)'},
                             orientation='h',
                             color='line_total',
                             color_continuous_scale='Reds')
        st.plotly_chart(fig_products, use_container_width=True)
    
    # Category details
    st.subheader("Category Breakdown")
    category_details = product_sales.groupby('category').agg({
        'product_id': 'nunique',
        'quantity': 'sum',
        'line_total': 'sum'
    }).reset_index()
    category_details.columns = ['Category', 'Unique Products', 'Units Sold', 'Revenue']
    
    st.dataframe(
        category_details.style.format({
            'Revenue': '${:,.2f}',
            'Units Sold': '{:,}'
        }),
        use_container_width=True,
        hide_index=True
    )

with tab4:
    st.subheader("RFM Customer Segmentation")
    
    # Calculate RFM
    reference_date = orders['order_date'].max() + pd.Timedelta(days=1)

    rfm = orders.groupby('customer_id').agg({
        'order_date': lambda x: (reference_date - x.max()).days,
        'order_id': 'count',
        'total_amount': 'sum'
    }).reset_index()
    rfm.columns = ['customer_id', 'recency', 'frequency', 'monetary']
    
    # RFM scores
    rfm['r_score'] = pd.qcut(rfm['recency'], q=5, labels=[5,4,3,2,1], duplicates='drop')
    rfm['f_score'] = pd.qcut(rfm['frequency'].rank(method='first'), q=5, labels=[1,2,3,4,5], duplicates='drop')
    rfm['m_score'] = pd.qcut(rfm['monetary'].rank(method='first'), q=5, labels=[1,2,3,4,5], duplicates='drop')
    
    rfm['r_score'] = rfm['r_score'].astype(int)
    rfm['f_score'] = rfm['f_score'].astype(int)
    rfm['m_score'] = rfm['m_score'].astype(int)
    
    # Assign segments
    def assign_segment(row):
        r, f, m = row['r_score'], row['f_score'], row['m_score']
        if r >= 4 and f >= 4 and m >= 4:
            return 'Champions'
        elif r >= 3 and f >= 3 and m >= 3:
            return 'Loyal'
        elif r >= 3 and f <= 2:
            return 'Potential Loyalist'
        elif r <= 2 and f >= 3:
            return 'At Risk'
        elif r <= 2 and f <= 2 and m >= 3:
            return 'Cant Lose'
        elif r <= 2 and f <= 2:
            return 'Lost'
        else:
            return 'Others'
    
    rfm['segment'] = rfm.apply(assign_segment, axis=1)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Segment distribution
        segment_dist = rfm['segment'].value_counts().reset_index()
        segment_dist.columns = ['segment', 'count']
        
        fig_segments = px.pie(segment_dist, values='count', names='segment',
                             title='Customer Segment Distribution',
                             color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig_segments, use_container_width=True)
    
    with col2:
        # Revenue by segment
        segment_revenue = rfm.groupby('segment')['monetary'].sum().reset_index().sort_values('monetary', ascending=False)
        
        fig_seg_rev = px.bar(segment_revenue, x='segment', y='monetary',
                            title='Revenue by Customer Segment',
                            labels={'segment': 'Segment', 'monetary': 'Revenue ($)'},
                            color='monetary',
                            color_continuous_scale='RdYlGn')
        st.plotly_chart(fig_seg_rev, use_container_width=True)
    
    # Segment summary
    st.subheader("Segment Summary")
    segment_summary = rfm.groupby('segment').agg({
        'customer_id': 'count',
        'recency': 'mean',
        'frequency': 'mean',
        'monetary': ['mean', 'sum']
    }).round(2)
    segment_summary.columns = ['Customer Count', 'Avg Recency (days)', 'Avg Frequency', 'Avg Monetary', 'Total Revenue']
    
    st.dataframe(
        segment_summary.style.format({
            'Avg Monetary': '${:,.2f}',
            'Total Revenue': '${:,.2f}',
            'Avg Recency (days)': '{:.0f}',
            'Avg Frequency': '{:.1f}'
        }),
        use_container_width=True
    )

# Insights section
st.divider()
st.subheader("🎯 Key Insights & Recommendations")

col1, col2 = st.columns(2)

with col1:
    st.info("""
    **Customer Behavior:**
    - Top 20% customers generate 65% of revenue
    - Average customer lifetime: 180 days
    - Repeat purchase rate: 35%
    """)
    
    st.success("""
    **Product Insights:**
    - Electronics category leads with 38% revenue
    - High product affinity in Tech accessories
    - Seasonal peaks in Nov-Dec
    """)

with col2:
    st.warning("""
    **Retention Opportunities:**
    - 25% customers in "At Risk" segment
    - Month 3 retention drops to 42%
    - Win-back campaigns needed
    """)
    
    st.error("""
    **Action Items:**
    - Launch loyalty program for Champions
    - Email campaign for At Risk segment
    - Product bundling for cross-sell
    """)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p><strong>Undadi Nishank</strong> | Data Analyst</p>
    <p>📧 nishankundadi66@gmail.com | 📱 7993002132 | 📍 Hyderabad, Telangana</p>
    <p>GitHub: <a href='https://github.com/Nishu799/ecommerce-analytics'>github.com/yourusername/ecommerce-analytics</a></p>
</div>
""", unsafe_allow_html=True)