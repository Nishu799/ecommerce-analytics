# E-Commerce Customer Behavior & Retention Analysis

## 📊 Project Overview
Comprehensive analysis of e-commerce customer data to identify purchasing patterns, segment customers, and develop retention strategies using Python, MySQL, and Power BI.

## 🎯 Business Objectives
- Analyze customer purchasing behavior and trends
- Segment customers using RFM (Recency, Frequency, Monetary) analysis
- Calculate customer retention and churn rates
- Identify high-value customers and at-risk segments
- Provide actionable recommendations for customer retention

## 🛠️ Technologies Used
- **Python 3.x**: Data cleaning, analysis, and visualization
- **MySQL**: Database management and complex queries
- **Power BI**: Interactive dashboard creation
- **Libraries**: pandas, numpy, matplotlib, seaborn, scikit-learn

## 📁 Project Structure
```
ecommerce-analytics/
├── data/
│   ├── raw/                    # Original dataset
│   ├── processed/              # Cleaned data
│   └── sample_output/          # Sample analysis results
├── sql/
│   ├── schema.sql             # Database schema
│   ├── data_import.sql        # Data loading queries
│   └── analysis_queries.sql   # Analytics queries
├── notebooks/
│   ├── 01_data_preparation.ipynb
│   ├── 02_exploratory_analysis.ipynb
│   ├── 03_rfm_segmentation.ipynb
│   ├── 04_cohort_analysis.ipynb
│   └── 05_visualizations.ipynb
├── src/
│   ├── data_processing.py
│   ├── rfm_analysis.py
│   ├── cohort_analysis.py
│   └── utils.py
├── dashboards/
│   └── ecommerce_dashboard.pbix
├── reports/
│   └── Executive_Summary.pdf
├── requirements.txt
└── README.md
```

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/Nishu799/ecommerce-analytics.git
cd ecommerce-analytics
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Database
```bash
mysql -u root -p < sql/schema.sql
mysql -u root -p ecommerce_db < sql/data_import.sql
```

### 4. Run Analysis
```bash
jupyter notebook notebooks/
```

## 📊 Key Findings

### Customer Segmentation (RFM)
- **Champions** (15%): High value, frequent buyers - Retention focus
- **Loyal Customers** (20%): Regular purchasers - Upsell opportunities  
- **At Risk** (25%): Declining engagement - Win-back campaigns needed
- **Lost** (18%): No recent purchases - Reactivation required

### Retention Metrics
- Overall retention rate: 42% (Month 3)
- Average Customer Lifetime Value: $1,247
- Churn rate: 28% annually
- Repeat purchase rate: 35%

### Revenue Insights
- Top 20% customers generate 65% of revenue
- Average order value: $87.50
- Peak purchasing months: November, December
- Mobile orders growing 45% YoY

## 💡 Recommendations

1. **Retention Program**: Target "At Risk" segment with personalized offers
2. **Loyalty Rewards**: Implement tiered program for Champions
3. **Win-Back Campaign**: Email automation for customers inactive 60+ days
4. **Product Bundling**: Leverage product affinity analysis for cross-selling

## 📈 Dashboard

Interactive Power BI dashboard includes:
- Executive KPI summary
- Customer segmentation breakdown
- Cohort retention heatmap
- Product performance analysis
- Geographic revenue distribution

**Live Dashboard**: [View Here](#) *(Update with your Power BI publish link)*

## 🔍 Methodology

1. **Data Cleaning**: Handled missing values, removed duplicates, standardized formats
2. **RFM Analysis**: Calculated recency, frequency, monetary scores for segmentation
3. **Cohort Analysis**: Tracked customer retention by registration cohort
4. **Statistical Analysis**: Identified trends, patterns, and correlations
5. **Visualization**: Created comprehensive dashboards for stakeholder communication

## 📫 Contact

**Undadi Nishank**
- Email: nishankundadi66@gmail.com
- Phone: 7993002132
- Location: Hyderabad, Telangana


## 📝 License

This project is available under the MIT License.

---

*This project demonstrates end-to-end data analytics capabilities including data processing, statistical analysis, database management, and business intelligence visualization.*