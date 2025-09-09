#!/usr/bin/env python3
"""
Purchase Price Analyzer
Analyzes and merges purchase price data from Excel sheets.
"""

import pandas as pd
import numpy as np
import logging
import os
from pathlib import Path
from typing import Tuple, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('price_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PriceAnalyzer:
    """Analyzes and merges purchase price data from Excel sheets."""
    
    def __init__(self, excel_path: str):
        """Initialize the analyzer with Excel file path."""
        self.excel_path = excel_path
        self.tabelle1_data = None
        self.bestand_data = None
        self.merged_data = None
        
    def load_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Load data from both Excel sheets."""
        try:
            logger.info(f"Loading data from {self.excel_path}")
            
            # Load Tabelle1 sheet
            self.tabelle1_data = pd.read_excel(
                self.excel_path, 
                sheet_name='Tabelle1',
                usecols=['Artnr', 'Fielmann EK']
            )
            logger.info(f"Loaded Tabelle1: {len(self.tabelle1_data)} rows")
            
            # Load Bestand Odoo sheet
            self.bestand_data = pd.read_excel(
                self.excel_path, 
                sheet_name='Bestand Odoo',
                usecols=['Interne Referenz', 'Kosten']
            )
            logger.info(f"Loaded Bestand Odoo: {len(self.bestand_data)} rows")
            
            return self.tabelle1_data, self.bestand_data
            
        except FileNotFoundError:
            logger.error(f"Excel file not found: {self.excel_path}")
            raise
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise
    
    def clean_data(self) -> None:
        """Clean and standardize the data."""
        logger.info("Cleaning and standardizing data...")
        
        # Clean Tabelle1 data
        if self.tabelle1_data is not None:
            # Rename columns for consistency
            self.tabelle1_data = self.tabelle1_data.rename(columns={
                'Artnr': 'article_number',
                'Fielmann EK': 'price'
            })
            
            # Clean article numbers
            self.tabelle1_data['article_number'] = (
                self.tabelle1_data['article_number']
                .astype(str)
                .str.strip()
                .str.replace(r'[^\w\-]', '', regex=True)  # Keep only alphanumeric and hyphens
            )
            
            # Clean prices - remove currency symbols and convert to numeric
            self.tabelle1_data['price'] = (
                self.tabelle1_data['price']
                .astype(str)
                .str.replace(r'[€$£¥\s]', '', regex=True)  # Remove currency symbols and spaces (but not comma)
                .str.replace(',', '.')  # Replace comma with dot for decimal
                .replace('', np.nan)  # Replace empty strings with NaN
            )
            # Convert to numeric, coercing errors to NaN
            self.tabelle1_data['price'] = pd.to_numeric(self.tabelle1_data['price'], errors='coerce')
            
            # Remove rows with missing article numbers or prices
            self.tabelle1_data = self.tabelle1_data.dropna(subset=['article_number', 'price'])
            self.tabelle1_data = self.tabelle1_data[self.tabelle1_data['article_number'] != '']
            
            # Handle duplicates: keep only the entry with the lowest price for each article
            initial_count = len(self.tabelle1_data)
            self.tabelle1_data = self.tabelle1_data.loc[
                self.tabelle1_data.groupby('article_number')['price'].idxmin()
            ].reset_index(drop=True)
            duplicates_removed = initial_count - len(self.tabelle1_data)
            
            if duplicates_removed > 0:
                logger.info(f"Removed {duplicates_removed} duplicate entries from Tabelle1, keeping lowest prices")
            
            logger.info(f"Tabelle1 after cleaning: {len(self.tabelle1_data)} rows")
        
        # Clean Bestand Odoo data
        if self.bestand_data is not None:
            # Rename columns for consistency
            self.bestand_data = self.bestand_data.rename(columns={
                'Interne Referenz': 'article_number',
                'Kosten': 'price'
            })
            
            # Clean article numbers
            self.bestand_data['article_number'] = (
                self.bestand_data['article_number']
                .astype(str)
                .str.strip()
                .str.replace(r'[^\w\-]', '', regex=True)
            )
            
            # Clean prices
            self.bestand_data['price'] = (
                self.bestand_data['price']
                .astype(str)
                .str.replace(r'[€$£¥\s]', '', regex=True)  # Remove currency symbols and spaces (but not comma)
                .str.replace(',', '.')
                .replace('', np.nan)
            )
            # Convert to numeric, coercing errors to NaN
            self.bestand_data['price'] = pd.to_numeric(self.bestand_data['price'], errors='coerce')
            
            # Remove rows with missing article numbers or prices
            self.bestand_data = self.bestand_data.dropna(subset=['article_number', 'price'])
            self.bestand_data = self.bestand_data[self.bestand_data['article_number'] != '']
            
            logger.info(f"Bestand Odoo after cleaning: {len(self.bestand_data)} rows")
    
    def analyze_duplicates_within_sheets(self) -> Dict[str, Any]:
        """Analyzes duplicates within each sheet for price variations."""
        logger.info("Analyzing duplicates within each sheet...")
        
        # Analyze duplicates in Tabelle1 (using original column names)
        tabelle1_duplicates = self._analyze_sheet_duplicates_raw(
            self.tabelle1_data, 'Tabelle1', 'Artnr', 'Fielmann EK'
        )
        
        # Analyze duplicates in Bestand Odoo (using original column names)
        bestand_duplicates = self._analyze_sheet_duplicates_raw(
            self.bestand_data, 'Bestand Odoo', 'Interne Referenz', 'Kosten'
        )
        
        return {
            'tabelle1': tabelle1_duplicates,
            'bestand_odoo': bestand_duplicates
        }

    def _analyze_sheet_duplicates_raw(self, df: pd.DataFrame, sheet_name: str, 
                                     article_col: str, price_col: str) -> Dict[str, Any]:
        """Helper function to analyze duplicates in a single dataframe with original column names."""
        if df is None:
            return {'total_duplicates': 0, 'duplicates_with_price_diff': 0, 'details': []}
        
        # Clean the data for analysis (similar to clean_data but without modifying the original)
        df_clean = df.copy()
        
        # Clean article numbers
        df_clean[article_col] = (
            df_clean[article_col]
            .astype(str)
            .str.strip()
            .str.replace(r'[^\w\-]', '', regex=True)
        )
        
        # Clean prices
        df_clean[price_col] = (
            df_clean[price_col]
            .astype(str)
            .str.replace(r'[€$£¥,\s]', '', regex=True)
            .str.replace(',', '.')
            .replace('', np.nan)
            .astype(float)
        )
        
        # Remove rows with missing article numbers or prices
        df_clean = df_clean.dropna(subset=[article_col, price_col])
        df_clean = df_clean[df_clean[article_col] != '']
        
        # Find all rows with duplicated article numbers
        duplicates = df_clean[df_clean[article_col].duplicated(keep=False)]
        
        if duplicates.empty:
            logger.info(f"No duplicates found in {sheet_name}")
            return {'total_duplicates': 0, 'duplicates_with_price_diff': 0, 'details': []}

        total_duplicates = duplicates[article_col].nunique()
        
        # Group by article number and check for price variations
        price_diff_details = []
        duplicates_with_price_diff = 0
        
        for article, group in duplicates.groupby(article_col):
            if group[price_col].nunique() > 1:
                duplicates_with_price_diff += 1
                price_diff_details.append({
                    'article_number': article,
                    'prices': sorted(list(group[price_col].unique())),
                    'price_mean': group[price_col].mean(),
                    'price_std': group[price_col].std(),
                    'price_min': group[price_col].min(),
                    'price_max': group[price_col].max(),
                })
                
        logger.info(f"Found {total_duplicates} articles with duplicates in {sheet_name}.")
        logger.info(f"{duplicates_with_price_diff} of them have different prices.")
        
        return {
            'total_duplicates': total_duplicates,
            'duplicates_with_price_diff': duplicates_with_price_diff,
            'details': price_diff_details
        }

    def _analyze_sheet_duplicates(self, df: pd.DataFrame, sheet_name: str) -> Dict[str, Any]:
        """Helper function to analyze duplicates in a single dataframe."""
        if df is None:
            return {'total_duplicates': 0, 'duplicates_with_price_diff': 0, 'details': []}
        
        # Find all rows with duplicated article numbers
        duplicates = df[df['article_number'].duplicated(keep=False)]
        
        if duplicates.empty:
            logger.info(f"No duplicates found in {sheet_name}")
            return {'total_duplicates': 0, 'duplicates_with_price_diff': 0, 'details': []}

        total_duplicates = duplicates['article_number'].nunique()
        
        # Group by article number and check for price variations
        price_diff_details = []
        duplicates_with_price_diff = 0
        
        for article, group in duplicates.groupby('article_number'):
            if group['price'].nunique() > 1:
                duplicates_with_price_diff += 1
                price_diff_details.append({
                    'article_number': article,
                    'prices': sorted(list(group['price'].unique())),
                    'price_mean': group['price'].mean(),
                    'price_std': group['price'].std(),
                    'price_min': group['price'].min(),
                    'price_max': group['price'].max(),
                })
                
        logger.info(f"Found {total_duplicates} articles with duplicates in {sheet_name}.")
        logger.info(f"{duplicates_with_price_diff} of them have different prices.")
        
        return {
            'total_duplicates': total_duplicates,
            'duplicates_with_price_diff': duplicates_with_price_diff,
            'details': price_diff_details
        }

    def analyze_common_articles(self) -> Dict[str, Any]:
        """Analyze common articles between both sheets."""
        logger.info("Analyzing common articles...")
        
        # Get unique article numbers from both sheets
        tabelle1_articles = set(self.tabelle1_data['article_number'].unique())
        bestand_articles = set(self.bestand_data['article_number'].unique())
        
        # Find common articles
        common_articles = tabelle1_articles.intersection(bestand_articles)
        
        # Calculate statistics
        total_tabelle1 = len(tabelle1_articles)
        total_bestand = len(bestand_articles)
        total_common = len(common_articles)
        
        overlap_tabelle1 = (total_common / total_tabelle1 * 100) if total_tabelle1 > 0 else 0
        overlap_bestand = (total_common / total_bestand * 100) if total_bestand > 0 else 0
        
        analysis = {
            'total_tabelle1_articles': total_tabelle1,
            'total_bestand_articles': total_bestand,
            'common_articles_count': total_common,
            'overlap_tabelle1_percentage': overlap_tabelle1,
            'overlap_bestand_percentage': overlap_bestand,
            'common_articles': list(common_articles)
        }
        
        logger.info(f"Common articles found: {total_common}")
        logger.info(f"Overlap with Tabelle1: {overlap_tabelle1:.2f}%")
        logger.info(f"Overlap with Bestand Odoo: {overlap_bestand:.2f}%")
        
        return analysis
    
    def analyze_price_differences(self) -> pd.DataFrame:
        """Analyze price differences for common articles."""
        logger.info("Analyzing price differences...")
        
        # Get common articles
        common_articles = set(self.tabelle1_data['article_number']).intersection(
            set(self.bestand_data['article_number'])
        )
        
        if not common_articles:
            logger.warning("No common articles found for price comparison")
            return pd.DataFrame()
        
        # Create comparison dataframe
        price_comparison = []
        
        for article in common_articles:
            tabelle1_price = self.tabelle1_data[
                self.tabelle1_data['article_number'] == article
            ]['price'].iloc[0]
            
            bestand_price = self.bestand_data[
                self.bestand_data['article_number'] == article
            ]['price'].iloc[0]
            
            price_diff = tabelle1_price - bestand_price
            price_diff_pct = (price_diff / bestand_price * 100) if bestand_price != 0 else 0
            
            price_comparison.append({
                'article_number': article,
                'tabelle1_price': tabelle1_price,
                'bestand_price': bestand_price,
                'price_difference': price_diff,
                'price_difference_pct': price_diff_pct
            })
        
        comparison_df = pd.DataFrame(price_comparison)
        
        # Generate statistics
        logger.info(f"Price comparison completed for {len(comparison_df)} articles")
        logger.info(f"Average price difference: {comparison_df['price_difference'].mean():.2f}")
        logger.info(f"Median price difference: {comparison_df['price_difference'].median():.2f}")
        logger.info(f"Average price difference %: {comparison_df['price_difference_pct'].mean():.2f}%")
        
        return comparison_df
    
    def merge_data(self) -> pd.DataFrame:
        """Merge data with Tabelle1 prices taking priority."""
        logger.info("Merging data...")
        
        # Start with Tabelle1 data (highest priority)
        merged = self.tabelle1_data.copy()
        merged['source'] = 'Tabelle1'
        
        # Add articles from Bestand Odoo that are not in Tabelle1
        bestand_only = self.bestand_data[
            ~self.bestand_data['article_number'].isin(merged['article_number'])
        ].copy()
        bestand_only['source'] = 'Bestand Odoo'
        
        # Combine both datasets
        self.merged_data = pd.concat([merged, bestand_only], ignore_index=True)
        
        # Add source information for common articles
        common_articles = set(self.tabelle1_data['article_number']).intersection(
            set(self.bestand_data['article_number'])
        )
        
        # Update source for common articles
        self.merged_data.loc[
            self.merged_data['article_number'].isin(common_articles), 
            'source'
        ] = 'Both (Tabelle1 priority)'
        
        logger.info(f"Merged data: {len(self.merged_data)} total articles")
        logger.info(f"From Tabelle1 only: {len(merged)} articles")
        logger.info(f"From Bestand Odoo only: {len(bestand_only)} articles")
        logger.info(f"Common articles (Tabelle1 priority): {len(common_articles)} articles")
        
        return self.merged_data
    
    def save_results(self, output_path: str) -> None:
        """Save the merged data to CSV."""
        if self.merged_data is None:
            logger.error("No merged data to save. Run merge_data() first.")
            return
        
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save to CSV
            self.merged_data.to_csv(output_path, index=False)
            logger.info(f"Results saved to {output_path}")
            
        except Exception as e:
            logger.error(f"Error saving results: {str(e)}")
            raise
    
    def generate_analytics_report(self, price_comparison: pd.DataFrame, duplicate_analysis: Dict[str, Any]) -> None:
        """Generate and display analytics report."""
        logger.info("Generating analytics report...")
        
        print("\n" + "="*60)
        print("PURCHASE PRICE ANALYSIS REPORT")
        print("="*60)
        
        # Basic statistics
        print(f"\n📊 DATA OVERVIEW:")
        print(f"   • Tabelle1 articles: {len(self.tabelle1_data):,}")
        print(f"   • Bestand Odoo articles: {len(self.bestand_data):,}")
        print(f"   • Common articles: {len(set(self.tabelle1_data['article_number']).intersection(set(self.bestand_data['article_number']))):,}")
        print(f"   • Final merged articles: {len(self.merged_data):,}")
        
        # Price analysis
        if not price_comparison.empty:
            print(f"\n💰 PRICE ANALYSIS:")
            print(f"   • Average price difference: €{price_comparison['price_difference'].mean():.2f}")
            print(f"   • Median price difference: €{price_comparison['price_difference'].median():.2f}")
            print(f"   • Average price change %: {price_comparison['price_difference_pct'].mean():.2f}%")
            print(f"   • Max price increase: €{price_comparison['price_difference'].max():.2f}")
            print(f"   • Max price decrease: €{price_comparison['price_difference'].min():.2f}")
            
            # Top price changes
            print(f"\n📈 TOP 5 PRICE INCREASES:")
            top_increases = price_comparison.nlargest(5, 'price_difference')
            for _, row in top_increases.iterrows():
                print(f"   • {row['article_number']}: €{row['bestand_price']:.2f} → €{row['tabelle1_price']:.2f} (+€{row['price_difference']:.2f}, +{row['price_difference_pct']:.1f}%)")
            
            print(f"\n📉 TOP 5 PRICE DECREASES:")
            top_decreases = price_comparison.nsmallest(5, 'price_difference')
            for _, row in top_decreases.iterrows():
                print(f"   • {row['article_number']}: €{row['bestand_price']:.2f} → €{row['tabelle1_price']:.2f} ({row['price_difference']:.2f}, {row['price_difference_pct']:.1f}%)")
        
        # Duplicate analysis
        print(f"\n🔬 DUPLICATE ANALYSIS:")
        
        # Tabelle1 duplicate report
        tabelle1_dupes = duplicate_analysis['tabelle1']
        print(f"\n   --- Tabelle1 Duplicates (Before Cleaning) ---")
        print(f"   • Articles with duplicates found: {tabelle1_dupes['total_duplicates']:,}")
        print(f"   • Duplicates with price differences: {tabelle1_dupes['duplicates_with_price_diff']:,}")
        if tabelle1_dupes['duplicates_with_price_diff'] > 0:
            print("   • Articles with price differences (lowest price was kept):")
            for detail in tabelle1_dupes['details'][:5]:
                prices_str = ", ".join([f"€{p:.2f}" for p in detail['prices']])
                print(f"     - {detail['article_number']}: Prices [{prices_str}] → Kept: €{detail['price_min']:.2f}")
        print(f"   • Resolution: Duplicates removed, lowest prices retained")

        # Bestand Odoo duplicate report
        bestand_dupes = duplicate_analysis['bestand_odoo']
        print(f"\n   --- Bestand Odoo Duplicates ---")
        print(f"   • Articles with duplicates: {bestand_dupes['total_duplicates']:,}")
        print(f"   • Duplicates with price differences: {bestand_dupes['duplicates_with_price_diff']:,}")
        if bestand_dupes['duplicates_with_price_diff'] > 0:
            print("   • Top 5 articles with price differences:")
            for detail in bestand_dupes['details'][:5]:
                prices_str = ", ".join([f"€{p:.2f}" for p in detail['prices']])
                print(f"     - {detail['article_number']}: Prices [{prices_str}]")
        
        # Data quality
        print(f"\n🔍 DATA QUALITY:")
        print(f"   • Missing prices in Tabelle1: {self.tabelle1_data['price'].isna().sum()}")
        print(f"   • Missing prices in Bestand Odoo: {self.bestand_data['price'].isna().sum()}")
        
        print("\n" + "="*60)

def main():
    """Main execution function."""
    # File paths
    excel_path = "data/purchase_price.xlsx"
    output_path = "data/final_purchase_price.csv"
    
    try:
        # Initialize analyzer
        analyzer = PriceAnalyzer(excel_path)
        
        # Load and clean data
        analyzer.load_data()
        
        # Analyze duplicates within each sheet (before cleaning to capture original duplicates)
        duplicate_analysis = analyzer.analyze_duplicates_within_sheets()
        
        analyzer.clean_data()
        
        # Analyze common articles
        common_analysis = analyzer.analyze_common_articles()
        
        # Analyze price differences
        price_comparison = analyzer.analyze_price_differences()
        
        # Merge data
        merged_data = analyzer.merge_data()
        
        # Save results
        analyzer.save_results(output_path)
        
        # Generate analytics report
        analyzer.generate_analytics_report(price_comparison, duplicate_analysis)
        
        logger.info("Analysis completed successfully!")
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
