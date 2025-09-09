#!/usr/bin/env python3
"""
Master Data Comparison Analyzer
Compares consolidated purchase prices with master product data.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import logging
import os
from pathlib import Path
from typing import Tuple, Dict, Any, List
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('master_data_comparison.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MasterDataComparison:
    """Compares consolidated purchase prices with master product data."""
    
    def __init__(self, consolidated_csv_path: str, master_excel_path: str):
        """Initialize the comparison analyzer."""
        self.consolidated_csv_path = consolidated_csv_path
        self.master_excel_path = master_excel_path
        self.consolidated_data = None
        self.master_data = None
        self.comparison_results = None
        
    def load_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Load data from both sources."""
        try:
            logger.info("Loading consolidated purchase price data...")
            self.consolidated_data = pd.read_csv(self.consolidated_csv_path)
            logger.info(f"Loaded consolidated data: {len(self.consolidated_data)} articles")
            
            logger.info("Loading master product data...")
            self.master_data = pd.read_excel(
                self.master_excel_path,
                usecols=['Product ID [sku]', 'Store Purchase Price [attribute6]']
            )
            logger.info(f"Loaded master data: {len(self.master_data)} articles")
            
            return self.consolidated_data, self.master_data
            
        except FileNotFoundError as e:
            logger.error(f"File not found: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise
    
    def clean_master_data(self) -> None:
        """Clean and process master data."""
        logger.info("Cleaning master data...")
        
        # Extract article numbers from Product ID [sku]
        # Format: <CategoryName>_<ArticleNumber>
        self.master_data['article_number'] = (
            self.master_data['Product ID [sku]']
            .astype(str)
            .str.extract(r'_(\d+)$')[0]  # Extract digits after the last underscore
        )
        
        # Clean and standardize article numbers
        self.master_data['article_number'] = (
            self.master_data['article_number']
            .str.strip()
            .str.replace(r'[^\w\-]', '', regex=True)
        )
        
        # Clean prices
        self.master_data['master_price'] = (
            self.master_data['Store Purchase Price [attribute6]']
            .astype(str)
            .str.replace(r'[€$£¥,\s]', '', regex=True)
            .str.replace(',', '.')
            .replace('', np.nan)
            .replace('nan', np.nan)
            .astype(float)
        )
        
        # Remove rows with missing article numbers or prices
        initial_count = len(self.master_data)
        self.master_data = self.master_data.dropna(subset=['article_number', 'master_price'])
        self.master_data = self.master_data[self.master_data['article_number'] != '']
        
        logger.info(f"Master data after cleaning: {len(self.master_data)} articles")
        logger.info(f"Removed {initial_count - len(self.master_data)} rows with missing data")
        
        # Show sample of extracted article numbers
        sample_extractions = self.master_data[['Product ID [sku]', 'article_number']].head(10)
        logger.info("Sample article number extractions:")
        for _, row in sample_extractions.iterrows():
            logger.info(f"  {row['Product ID [sku]']} → {row['article_number']}")
    
    def compare_articles(self) -> Dict[str, Any]:
        """Compare articles between consolidated and master data."""
        logger.info("Comparing articles between datasets...")
        
        # Get article sets - ensure both are strings for proper comparison
        consolidated_articles = set(self.consolidated_data['article_number'].astype(str).unique())
        master_articles = set(self.master_data['article_number'].astype(str).unique())
        
        # Find overlaps and differences
        common_articles = consolidated_articles.intersection(master_articles)
        missing_in_master = consolidated_articles - master_articles
        extra_in_master = master_articles - consolidated_articles
        
        logger.info(f"Articles in consolidated data: {len(consolidated_articles):,}")
        logger.info(f"Articles in master data: {len(master_articles):,}")
        logger.info(f"Common articles: {len(common_articles):,}")
        logger.info(f"Missing in master data: {len(missing_in_master):,}")
        logger.info(f"Extra in master data: {len(extra_in_master):,}")
        
        return {
            'consolidated_articles': consolidated_articles,
            'master_articles': master_articles,
            'common_articles': common_articles,
            'missing_in_master': missing_in_master,
            'extra_in_master': extra_in_master
        }
    
    def analyze_price_discrepancies(self, common_articles: set) -> pd.DataFrame:
        """Analyze price discrepancies for common articles."""
        logger.info("Analyzing price discrepancies...")
        
        if not common_articles:
            logger.warning("No common articles found for price comparison")
            return pd.DataFrame()
        
        # Create comparison dataframe
        price_comparisons = []
        
        for article in common_articles:
            # Get consolidated price (should be unique after our cleaning)
            consolidated_price = self.consolidated_data[
                self.consolidated_data['article_number'].astype(str) == article
            ]['price'].iloc[0]
            
            # Get master price (take first if multiple entries)
            master_price = self.master_data[
                self.master_data['article_number'].astype(str) == article
            ]['master_price'].iloc[0]
            
            price_diff = consolidated_price - master_price
            price_diff_pct = (price_diff / master_price * 100) if master_price != 0 else 0
            
            price_comparisons.append({
                'article_number': article,
                'consolidated_price': consolidated_price,
                'master_price': master_price,
                'price_difference': price_diff,
                'price_difference_pct': price_diff_pct,
                'has_discrepancy': abs(price_diff) > 0.01  # Consider differences > 1 cent as discrepancies
            })
        
        comparison_df = pd.DataFrame(price_comparisons)
        
        # Calculate statistics
        discrepancies = comparison_df[comparison_df['has_discrepancy']]
        
        logger.info(f"Price comparison completed for {len(comparison_df)} articles")
        logger.info(f"Articles with price discrepancies: {len(discrepancies)} ({len(discrepancies)/len(comparison_df)*100:.1f}%)")
        logger.info(f"Average price difference: €{comparison_df['price_difference'].mean():.2f}")
        logger.info(f"Median price difference: €{comparison_df['price_difference'].median():.2f}")
        logger.info(f"Max price difference: €{comparison_df['price_difference'].max():.2f}")
        logger.info(f"Min price difference: €{comparison_df['price_difference'].min():.2f}")
        
        return comparison_df
    
    def generate_visualizations(self, comparison_df: pd.DataFrame, output_dir: str = "data/plots") -> None:
        """Generate visualizations for price discrepancies."""
        logger.info("Generating visualizations...")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Set style
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Check if we have data to visualize
        if comparison_df.empty:
            logger.warning("No price comparison data available for visualization")
            # Create a simple summary plot
            plt.figure(figsize=(8, 6))
            plt.text(0.5, 0.5, 'No Common Articles Found\nfor Price Comparison', 
                    ha='center', va='center', fontsize=16, 
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
            plt.xlim(0, 1)
            plt.ylim(0, 1)
            plt.axis('off')
            plt.title('Price Comparison Analysis', fontsize=18, fontweight='bold')
            plt.savefig(f'{output_dir}/no_comparison_data.png', dpi=300, bbox_inches='tight')
            plt.close()
            return
        
        # 1. Price Difference Distribution
        plt.figure(figsize=(12, 8))
        plt.subplot(2, 2, 1)
        comparison_df['price_difference'].hist(bins=50, alpha=0.7, color='skyblue', edgecolor='black')
        plt.title('Distribution of Price Differences\n(Ecomm_PurchasePrice - Pricefx_PurchasePrice)', fontsize=12, fontweight='bold')
        plt.xlabel('Price Difference (€)')
        plt.ylabel('Frequency')
        plt.axvline(0, color='red', linestyle='--', alpha=0.7, label='No Difference')
        plt.legend()
        
        # 2. Price Difference Percentage Distribution
        plt.subplot(2, 2, 2)
        comparison_df['price_difference_pct'].hist(bins=50, alpha=0.7, color='lightcoral', edgecolor='black')
        plt.title('Distribution of Price Differences (%)', fontsize=12, fontweight='bold')
        plt.xlabel('Price Difference (%)')
        plt.ylabel('Frequency')
        plt.axvline(0, color='red', linestyle='--', alpha=0.7, label='No Difference')
        plt.legend()
        
        # 3. Scatter Plot: Ecomm_PurchasePrice vs Pricefx_PurchasePrice Prices
        plt.subplot(2, 2, 3)
        plt.scatter(comparison_df['master_price'], comparison_df['consolidated_price'], 
                   alpha=0.6, s=20, color='green')
        
        # Add diagonal line for perfect match
        max_price = max(comparison_df['master_price'].max(), comparison_df['consolidated_price'].max())
        plt.plot([0, max_price], [0, max_price], 'r--', alpha=0.7, label='Perfect Match')
        
        plt.title('Ecomm_PurchasePrice vs Pricefx_PurchasePrice', fontsize=12, fontweight='bold')
        plt.xlabel('Pricefx_PurchasePrice (€)')
        plt.ylabel('Ecomm_PurchasePrice (€)')
        plt.legend()
        
        # 4. Articles with Discrepancies
        plt.subplot(2, 2, 4)
        discrepancy_counts = comparison_df['has_discrepancy'].value_counts()
        labels = ['No Discrepancy', 'Has Discrepancy']
        colors = ['lightgreen', 'orange']
        plt.pie(discrepancy_counts.values, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        plt.title('Articles with Price Discrepancies', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/price_comparison_overview.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 5. Top Discrepancies Bar Chart
        if len(comparison_df[comparison_df['has_discrepancy']]) > 0:
            plt.figure(figsize=(14, 8))
            
            # Top 20 largest positive discrepancies
            plt.subplot(1, 2, 1)
            top_positive = comparison_df.nlargest(20, 'price_difference')
            plt.barh(range(len(top_positive)), top_positive['price_difference'], color='red', alpha=0.7)
            plt.yticks(range(len(top_positive)), top_positive['article_number'])
            plt.title('Top 20 Largest Price Increases\n(Ecomm_PurchasePrice > Pricefx_PurchasePrice)', fontsize=12, fontweight='bold')
            plt.xlabel('Price Difference (€)')
            
            # Top 20 largest negative discrepancies
            plt.subplot(1, 2, 2)
            top_negative = comparison_df.nsmallest(20, 'price_difference')
            plt.barh(range(len(top_negative)), top_negative['price_difference'], color='blue', alpha=0.7)
            plt.yticks(range(len(top_negative)), top_negative['article_number'])
            plt.title('Top 20 Largest Price Decreases\n(Ecomm_PurchasePrice < Pricefx_PurchasePrice)', fontsize=12, fontweight='bold')
            plt.xlabel('Price Difference (€)')
            
            plt.tight_layout()
            plt.savefig(f'{output_dir}/top_discrepancies.png', dpi=300, bbox_inches='tight')
            plt.close()
        
        logger.info(f"Visualizations saved to {output_dir}/")
    
    def generate_report(self, comparison_results: Dict[str, Any], 
                       price_comparison_df: pd.DataFrame) -> None:
        """Generate comprehensive comparison report."""
        logger.info("Generating comparison report...")
        
        print("\n" + "="*80)
        print("MASTER DATA COMPARISON REPORT")
        print("="*80)
        
        # Data Overview
        print(f"\n📊 DATA OVERVIEW:")
        print(f"   • Consolidated articles: {len(comparison_results['consolidated_articles']):,}")
        print(f"   • Master data articles: {len(comparison_results['master_articles']):,}")
        print(f"   • Common articles: {len(comparison_results['common_articles']):,}")
        print(f"   • Coverage: {len(comparison_results['common_articles'])/len(comparison_results['consolidated_articles'])*100:.1f}%")
        
        # Missing Articles
        missing_count = len(comparison_results['missing_in_master'])
        print(f"\n❌ MISSING ARTICLES IN MASTER DATA:")
        print(f"   • Count: {missing_count:,}")
        print(f"   • Percentage: {missing_count/len(comparison_results['consolidated_articles'])*100:.1f}%")
        
        if missing_count > 0 and missing_count <= 20:
            print("   • Missing article numbers:")
            for article in sorted(list(comparison_results['missing_in_master'])[:20]):
                print(f"     - {article}")
        elif missing_count > 20:
            print("   • First 20 missing article numbers:")
            for article in sorted(list(comparison_results['missing_in_master'])[:20]):
                print(f"     - {article}")
            print(f"     ... and {missing_count - 20} more")
        
        # Price Analysis
        if not price_comparison_df.empty:
            discrepancies = price_comparison_df[price_comparison_df['has_discrepancy']]
            
            print(f"\n💰 PRICE ANALYSIS:")
            print(f"   • Articles compared: {len(price_comparison_df):,}")
            print(f"   • Articles with discrepancies: {len(discrepancies):,} ({len(discrepancies)/len(price_comparison_df)*100:.1f}%)")
            print(f"   • Average price difference: €{price_comparison_df['price_difference'].mean():.2f}")
            print(f"   • Median price difference: €{price_comparison_df['price_difference'].median():.2f}")
            print(f"   • Standard deviation: €{price_comparison_df['price_difference'].std():.2f}")
            print(f"   • Max price increase: €{price_comparison_df['price_difference'].max():.2f}")
            print(f"   • Max price decrease: €{price_comparison_df['price_difference'].min():.2f}")
            
            if len(discrepancies) > 0:
                print(f"\n📈 TOP 10 PRICE INCREASES:")
                top_increases = discrepancies.nlargest(10, 'price_difference')
                for _, row in top_increases.iterrows():
                    print(f"   • {row['article_number']}: €{row['master_price']:.2f} → €{row['consolidated_price']:.2f} (+€{row['price_difference']:.2f}, +{row['price_difference_pct']:.1f}%)")
                
                print(f"\n📉 TOP 10 PRICE DECREASES:")
                top_decreases = discrepancies.nsmallest(10, 'price_difference')
                for _, row in top_decreases.iterrows():
                    print(f"   • {row['article_number']}: €{row['master_price']:.2f} → €{row['consolidated_price']:.2f} ({row['price_difference']:.2f}, {row['price_difference_pct']:.1f}%)")
        
        print("\n" + "="*80)
    
    def save_detailed_results(self, comparison_results: Dict[str, Any], 
                            price_comparison_df: pd.DataFrame, 
                            output_dir: str = "data") -> None:
        """Save detailed results to CSV files."""
        logger.info("Saving detailed results...")
        
        # Save missing articles
        if comparison_results['missing_in_master']:
            missing_df = pd.DataFrame({
                'missing_article_numbers': sorted(list(comparison_results['missing_in_master']))
            })
            missing_df.to_csv(f"{output_dir}/missing_articles_in_master.csv", index=False)
            logger.info(f"Missing articles saved to {output_dir}/missing_articles_in_master.csv")
        
        # Save price comparison results
        if not price_comparison_df.empty:
            price_comparison_df.to_csv(f"{output_dir}/price_comparison_results.csv", index=False)
            logger.info(f"Price comparison results saved to {output_dir}/price_comparison_results.csv")
            
            # Save only discrepancies
            discrepancies = price_comparison_df[price_comparison_df['has_discrepancy']]
            if len(discrepancies) > 0:
                discrepancies.to_csv(f"{output_dir}/price_discrepancies_only.csv", index=False)
                logger.info(f"Price discrepancies saved to {output_dir}/price_discrepancies_only.csv")

def main():
    """Main execution function."""
    # File paths
    consolidated_csv = "data/final_purchase_price.csv"
    master_excel = "data/PurchasePriceCost-2025-09-09T15-41-13.xlsx"
    
    try:
        # Initialize comparison analyzer
        analyzer = MasterDataComparison(consolidated_csv, master_excel)
        
        # Load data
        analyzer.load_data()
        
        # Clean master data
        analyzer.clean_master_data()
        
        # Compare articles
        comparison_results = analyzer.compare_articles()
        
        # Analyze price discrepancies
        price_comparison_df = analyzer.analyze_price_discrepancies(
            comparison_results['common_articles']
        )
        
        # Generate visualizations
        analyzer.generate_visualizations(price_comparison_df)
        
        # Generate report
        analyzer.generate_report(comparison_results, price_comparison_df)
        
        # Save detailed results
        analyzer.save_detailed_results(comparison_results, price_comparison_df)
        
        logger.info("Master data comparison completed successfully!")
        
    except Exception as e:
        logger.error(f"Comparison analysis failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
