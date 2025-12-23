"""
Cohort Analysis Module
Author: Undadi Nishank
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

class CohortAnalysis:
    def __init__(self, orders_df):
        """Initialize cohort analysis with orders data"""
        self.orders = orders_df.copy()
        self.orders['order_date'] = pd.to_datetime(self.orders['order_date'])
        self.cohort_data = None
        
    def create_cohorts(self):
        """Create cohort groups based on first purchase date"""
        # Get first purchase date for each customer
        first_purchase = self.orders.groupby('customer_id')['order_date'].min().reset_index()
        first_purchase.columns = ['customer_id', 'cohort_date']
        first_purchase['cohort_month'] = first_purchase['cohort_date'].dt.to_period('M')
        
        # Merge with orders
        cohort_data = self.orders.merge(first_purchase[['customer_id', 'cohort_month']], 
                                       on='customer_id')
        
        # Calculate order month
        cohort_data['order_month'] = cohort_data['order_date'].dt.to_period('M')
        
        # Calculate cohort index (months since first purchase)
        cohort_data['cohort_index'] = (cohort_data['order_month'] - 
                                       cohort_data['cohort_month']).apply(lambda x: x.n)
        
        self.cohort_data = cohort_data
        return cohort_data
    
    def calculate_retention(self):
        """Calculate retention rates by cohort"""
        if self.cohort_data is None:
            self.create_cohorts()
        
        # Count unique customers in each cohort-period
        cohort_pivot = self.cohort_data.groupby(['cohort_month', 'cohort_index'])\
                           .agg({'customer_id': pd.Series.nunique})\
                           .reset_index()
        
        # Pivot to wide format
        cohort_table = cohort_pivot.pivot(index='cohort_month', 
                                          columns='cohort_index', 
                                          values='customer_id')
        
        # Calculate retention rates
        cohort_size = cohort_table.iloc[:, 0]
        retention_table = cohort_table.divide(cohort_size, axis=0) * 100
        
        return cohort_table, retention_table
    
    def plot_retention_heatmap(self, save_path=None):
        """Plot retention rate heatmap"""
        cohort_table, retention_table = self.calculate_retention()
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        sns.heatmap(retention_table, annot=True, fmt='.1f', cmap='RdYlGn', 
                   ax=ax, vmin=0, vmax=100, cbar_kws={'label': 'Retention Rate (%)'})
        
        ax.set_title('Cohort Retention Rate (%)', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Cohort Index (Months since first purchase)', fontsize=12)
        ax.set_ylabel('Cohort Month', fontsize=12)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
        
        return retention_table
    
    def calculate_cohort_metrics(self):
        """Calculate various cohort metrics"""
        if self.cohort_data is None:
            self.create_cohorts()
        
        metrics = self.cohort_data.groupby(['cohort_month', 'cohort_index']).agg({
            'customer_id': pd.Series.nunique,
            'order_id': 'count',
            'total_amount': 'sum'
        }).reset_index()
        
        metrics.columns = ['cohort_month', 'cohort_index', 'customers', 
                          'orders', 'revenue']
        
        # Calculate average revenue per customer
        metrics['avg_revenue_per_customer'] = (metrics['revenue'] / 
                                               metrics['customers']).round(2)
        
        return metrics
    
    def plot_cohort_revenue(self, save_path=None):
        """Plot cumulative revenue by cohort"""
        metrics = self.calculate_cohort_metrics()
        
        # Calculate cumulative revenue
        cumulative_revenue = metrics.pivot(index='cohort_month', 
                                          columns='cohort_index', 
                                          values='revenue').fillna(0)
        cumulative_revenue = cumulative_revenue.cumsum(axis=1)
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        for cohort in cumulative_revenue.index[-10:]:  # Plot last 10 cohorts
            ax.plot(cumulative_revenue.columns, 
                   cumulative_revenue.loc[cohort], 
                   marker='o', label=str(cohort))
        
        ax.set_title('Cumulative Revenue by Cohort', fontsize=16, fontweight='bold')
        ax.set_xlabel('Cohort Index (Months)', fontsize=12)
        ax.set_ylabel('Cumulative Revenue ($)', fontsize=12)
        ax.legend(title='Cohort Month', bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def get_retention_summary(self):
        """Get retention summary statistics"""
        cohort_table, retention_table = self.calculate_retention()
        
        summary = {
            'month_1_retention': retention_table[1].mean(),
            'month_3_retention': retention_table[3].mean() if 3 in retention_table.columns else None,
            'month_6_retention': retention_table[6].mean() if 6 in retention_table.columns else None,
            'month_12_retention': retention_table[12].mean() if 12 in retention_table.columns else None,
            'avg_cohort_size': cohort_table[0].mean()
        }
        
        return summary
    
    def export_results(self, output_path):
        """Export cohort data to CSV"""
        if self.cohort_data is None:
            self.create_cohorts()
        
        self.cohort_data.to_csv(output_path, index=False)
        print(f"Cohort data exported to {output_path}")

# Example usage
if __name__ == "__main__":
    # Load data
    orders = pd.read_csv('data/raw/orders.csv')
    
    # Perform cohort analysis
    cohort = CohortAnalysis(orders)
    cohort.create_cohorts()
    
    # Plot retention heatmap
    retention_table = cohort.plot_retention_heatmap(
        save_path='data/sample_output/cohort_retention.png'
    )
    
    # Plot cumulative revenue
    cohort.plot_cohort_revenue(
        save_path='data/sample_output/cohort_revenue.png'
    )
    
    # Get summary
    summary = cohort.get_retention_summary()
    print("\nRetention Summary:")
    for key, value in summary.items():
        if value is not None:
            print(f"{key}: {value:.2f}%")
    
    # Export results
    cohort.export_results('data/processed/cohort_data.csv')