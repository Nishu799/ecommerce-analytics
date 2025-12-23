"""
RFM Analysis Module
Author: Undadi Nishank
"""

import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

class RFMAnalysis:
    def __init__(self, orders_df, customers_df):
        """Initialize RFM analysis with orders and customers data"""
        self.orders = orders_df.copy()
        self.customers = customers_df.copy()
        self.rfm_data = None
        
    def calculate_rfm(self, reference_date=None):
        """Calculate RFM scores for all customers"""
        if reference_date is None:
            reference_date = pd.to_datetime(self.orders['order_date']).max()
        
        # Convert order_date to datetime
        self.orders['order_date'] = pd.to_datetime(self.orders['order_date'])
        
        # Calculate RFM metrics
        rfm = self.orders.groupby('customer_id').agg({
            'order_date': lambda x: (reference_date - x.max()).days,  # Recency
            'order_id': 'count',  # Frequency
            'total_amount': 'sum'  # Monetary
        }).reset_index()
        
        rfm.columns = ['customer_id', 'recency', 'frequency', 'monetary']
        
        # Calculate RFM scores (1-5 scale)
        rfm['r_score'] = pd.qcut(rfm['recency'], q=5, labels=[5,4,3,2,1], duplicates='drop')
        rfm['f_score'] = pd.qcut(rfm['frequency'].rank(method='first'), q=5, labels=[1,2,3,4,5], duplicates='drop')
        rfm['m_score'] = pd.qcut(rfm['monetary'].rank(method='first'), q=5, labels=[1,2,3,4,5], duplicates='drop')
        
        # Convert scores to integers
        rfm['r_score'] = rfm['r_score'].astype(int)
        rfm['f_score'] = rfm['f_score'].astype(int)
        rfm['m_score'] = rfm['m_score'].astype(int)
        
        # Create RFM segment
        rfm['rfm_segment'] = rfm.apply(self._assign_segment, axis=1)
        
        # Merge with customer info
        rfm = rfm.merge(self.customers[['customer_id', 'customer_name', 'country']], 
                       on='customer_id', how='left')
        
        self.rfm_data = rfm
        return rfm
    
    def _assign_segment(self, row):
        """Assign customer segment based on RFM scores"""
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
    
    def get_segment_summary(self):
        """Get summary statistics by segment"""
        if self.rfm_data is None:
            raise ValueError("Run calculate_rfm() first")
        
        summary = self.rfm_data.groupby('rfm_segment').agg({
            'customer_id': 'count',
            'recency': 'mean',
            'frequency': 'mean',
            'monetary': ['mean', 'sum']
        }).round(2)
        
        summary.columns = ['customer_count', 'avg_recency', 'avg_frequency', 
                          'avg_monetary', 'total_revenue']
        summary = summary.reset_index()
        summary['revenue_percentage'] = (summary['total_revenue'] / 
                                        summary['total_revenue'].sum() * 100).round(2)
        
        return summary
    
    def plot_rfm_distribution(self, save_path=None):
        """Plot RFM distribution visualizations"""
        if self.rfm_data is None:
            raise ValueError("Run calculate_rfm() first")
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Segment distribution
        segment_counts = self.rfm_data['rfm_segment'].value_counts()
        axes[0, 0].pie(segment_counts.values, labels=segment_counts.index, autopct='%1.1f%%')
        axes[0, 0].set_title('Customer Segment Distribution', fontsize=14, fontweight='bold')
        
        # Revenue by segment
        segment_revenue = self.rfm_data.groupby('rfm_segment')['monetary'].sum().sort_values(ascending=False)
        axes[0, 1].bar(range(len(segment_revenue)), segment_revenue.values)
        axes[0, 1].set_xticks(range(len(segment_revenue)))
        axes[0, 1].set_xticklabels(segment_revenue.index, rotation=45, ha='right')
        axes[0, 1].set_title('Total Revenue by Segment', fontsize=14, fontweight='bold')
        axes[0, 1].set_ylabel('Revenue ($)')
        
        # RFM score distribution
        rfm_scores = pd.DataFrame({
            'Recency': self.rfm_data['r_score'],
            'Frequency': self.rfm_data['f_score'],
            'Monetary': self.rfm_data['m_score']
        })
        rfm_scores.boxplot(ax=axes[1, 0])
        axes[1, 0].set_title('RFM Score Distribution', fontsize=14, fontweight='bold')
        axes[1, 0].set_ylabel('Score (1-5)')
        
        # Frequency vs Monetary scatter
        for segment in self.rfm_data['rfm_segment'].unique():
            segment_data = self.rfm_data[self.rfm_data['rfm_segment'] == segment]
            axes[1, 1].scatter(segment_data['frequency'], segment_data['monetary'], 
                             label=segment, alpha=0.6, s=50)
        axes[1, 1].set_xlabel('Frequency (Orders)')
        axes[1, 1].set_ylabel('Monetary ($)')
        axes[1, 1].set_title('Frequency vs Monetary by Segment', fontsize=14, fontweight='bold')
        axes[1, 1].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def export_results(self, output_path):
        """Export RFM results to CSV"""
        if self.rfm_data is None:
            raise ValueError("Run calculate_rfm() first")
        
        self.rfm_data.to_csv(output_path, index=False)
        print(f"RFM results exported to {output_path}")

# Example usage
if __name__ == "__main__":
    # Load data
    orders = pd.read_csv('data/raw/orders.csv')
    customers = pd.read_csv('data/raw/customers.csv')
    
    # Perform RFM analysis
    rfm = RFMAnalysis(orders, customers)
    rfm_results = rfm.calculate_rfm()
    
    # Get summary
    summary = rfm.get_segment_summary()
    print("\nRFM Segment Summary:")
    print(summary)
    
    # Plot visualizations
    rfm.plot_rfm_distribution(save_path='data/sample_output/rfm_analysis.png')
    
    # Export results
    rfm.export_results('data/processed/rfm_scores.csv')