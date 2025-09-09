#!/usr/bin/env python3
"""
Unit tests for the PriceAnalyzer class.
"""

import unittest
import pandas as pd
import numpy as np
import tempfile
import os
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from price_analyzer import PriceAnalyzer


class TestPriceAnalyzer(unittest.TestCase):
    """Test cases for PriceAnalyzer class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.excel_path = os.path.join(self.temp_dir, "test_data.xlsx")
        
        # Create test data
        self.tabelle1_data = pd.DataFrame({
            'Artnr': ['ART001', 'ART002', 'ART003', 'ART004', 'ART005'],
            'Fielmann EK': ['15.50€', '25,75', '35.00', '45.25', 'invalid']
        })
        
        self.bestand_data = pd.DataFrame({
            'Interne Referenz': ['ART001', 'ART002', 'ART006', 'ART007', 'ART008'],
            'Kosten': ['14.50', '24,75€', '65.75', '75.00', '']
        })
        
        # Create test Excel file
        with pd.ExcelWriter(self.excel_path, engine='openpyxl') as writer:
            self.tabelle1_data.to_excel(writer, sheet_name='Tabelle1', index=False)
            self.bestand_data.to_excel(writer, sheet_name='Bestand Odoo', index=False)
        
        self.analyzer = PriceAnalyzer(self.excel_path)

    def tearDown(self):
        """Clean up after each test method."""
        # Remove temporary files
        if os.path.exists(self.excel_path):
            os.remove(self.excel_path)
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init(self):
        """Test PriceAnalyzer initialization."""
        analyzer = PriceAnalyzer("test_path.xlsx")
        self.assertEqual(analyzer.excel_path, "test_path.xlsx")
        self.assertIsNone(analyzer.tabelle1_data)
        self.assertIsNone(analyzer.bestand_data)
        self.assertIsNone(analyzer.merged_data)

    def test_load_data_success(self):
        """Test successful data loading."""
        tabelle1, bestand = self.analyzer.load_data()
        
        # Check data was loaded
        self.assertIsNotNone(self.analyzer.tabelle1_data)
        self.assertIsNotNone(self.analyzer.bestand_data)
        
        # Check returned dataframes
        self.assertEqual(len(tabelle1), 5)
        self.assertEqual(len(bestand), 5)
        
        # Check column names
        self.assertIn('Artnr', tabelle1.columns)
        self.assertIn('Fielmann EK', tabelle1.columns)
        self.assertIn('Interne Referenz', bestand.columns)
        self.assertIn('Kosten', bestand.columns)

    def test_load_data_file_not_found(self):
        """Test loading data when file doesn't exist."""
        analyzer = PriceAnalyzer("nonexistent_file.xlsx")
        
        with self.assertRaises(FileNotFoundError):
            analyzer.load_data()

    def test_load_data_invalid_sheet(self):
        """Test loading data with invalid sheet names."""
        # Create Excel file without required sheets
        test_path = os.path.join(self.temp_dir, "invalid_sheets.xlsx")
        pd.DataFrame({'col1': [1, 2, 3]}).to_excel(test_path, sheet_name='WrongSheet', index=False)
        
        analyzer = PriceAnalyzer(test_path)
        
        with self.assertRaises(Exception):
            analyzer.load_data()
        
        os.remove(test_path)

    def test_clean_data(self):
        """Test data cleaning functionality."""
        # Load data first
        self.analyzer.load_data()
        
        # Clean data
        self.analyzer.clean_data()
        
        # Check Tabelle1 cleaning
        tabelle1 = self.analyzer.tabelle1_data
        self.assertIn('article_number', tabelle1.columns)
        self.assertIn('price', tabelle1.columns)
        
        # Check that prices are numeric
        self.assertTrue(pd.api.types.is_numeric_dtype(tabelle1['price']))
        
        # Check that invalid prices are removed
        self.assertFalse(tabelle1['price'].isna().all())
        
        # Check Bestand cleaning
        bestand = self.analyzer.bestand_data
        self.assertIn('article_number', bestand.columns)
        self.assertIn('price', bestand.columns)
        
        # Check that prices are numeric
        self.assertTrue(pd.api.types.is_numeric_dtype(bestand['price']))

    def test_clean_data_price_conversion(self):
        """Test specific price conversion scenarios."""
        # Load and clean data
        self.analyzer.load_data()
        self.analyzer.clean_data()
        
        # Check specific price conversions
        tabelle1 = self.analyzer.tabelle1_data
        bestand = self.analyzer.bestand_data
        
        # Verify Euro symbol removal and comma to dot conversion
        art001_tabelle1 = tabelle1[tabelle1['article_number'] == 'ART001']['price'].iloc[0]
        self.assertEqual(art001_tabelle1, 15.50)
        
        art002_tabelle1 = tabelle1[tabelle1['article_number'] == 'ART002']['price'].iloc[0]
        self.assertEqual(art002_tabelle1, 25.75)

    def test_analyze_common_articles(self):
        """Test analysis of common articles."""
        # Prepare data
        self.analyzer.load_data()
        self.analyzer.clean_data()
        
        # Analyze common articles
        analysis = self.analyzer.analyze_common_articles()
        
        # Check analysis structure
        expected_keys = [
            'total_tabelle1_articles', 'total_bestand_articles', 
            'common_articles_count', 'overlap_tabelle1_percentage',
            'overlap_bestand_percentage', 'common_articles'
        ]
        
        for key in expected_keys:
            self.assertIn(key, analysis)
        
        # Check common articles (ART001 and ART002 should be common)
        self.assertEqual(analysis['common_articles_count'], 2)
        self.assertIn('ART001', analysis['common_articles'])
        self.assertIn('ART002', analysis['common_articles'])

    def test_analyze_common_articles_empty_data(self):
        """Test common articles analysis with empty data."""
        # Create analyzer with empty data
        self.analyzer.tabelle1_data = pd.DataFrame(columns=['article_number', 'price'])
        self.analyzer.bestand_data = pd.DataFrame(columns=['article_number', 'price'])
        
        analysis = self.analyzer.analyze_common_articles()
        
        self.assertEqual(analysis['common_articles_count'], 0)
        self.assertEqual(analysis['total_tabelle1_articles'], 0)
        self.assertEqual(analysis['total_bestand_articles'], 0)

    def test_analyze_price_differences(self):
        """Test price difference analysis."""
        # Prepare data
        self.analyzer.load_data()
        self.analyzer.clean_data()
        
        # Analyze price differences
        price_comparison = self.analyzer.analyze_price_differences()
        
        # Check structure
        expected_columns = [
            'article_number', 'tabelle1_price', 'bestand_price',
            'price_difference', 'price_difference_pct'
        ]
        
        for col in expected_columns:
            self.assertIn(col, price_comparison.columns)
        
        # Check that we have comparisons for common articles
        self.assertEqual(len(price_comparison), 2)  # ART001 and ART002
        
        # Check specific calculations
        art001_row = price_comparison[price_comparison['article_number'] == 'ART001'].iloc[0]
        self.assertEqual(art001_row['tabelle1_price'], 15.50)
        self.assertEqual(art001_row['bestand_price'], 14.50)
        self.assertEqual(art001_row['price_difference'], 1.00)

    def test_analyze_price_differences_no_common_articles(self):
        """Test price difference analysis with no common articles."""
        # Create data with no common articles
        self.analyzer.tabelle1_data = pd.DataFrame({
            'article_number': ['ART001', 'ART002'],
            'price': [10.0, 20.0]
        })
        self.analyzer.bestand_data = pd.DataFrame({
            'article_number': ['ART003', 'ART004'],
            'price': [30.0, 40.0]
        })
        
        price_comparison = self.analyzer.analyze_price_differences()
        
        # Should return empty DataFrame
        self.assertTrue(price_comparison.empty)

    def test_merge_data(self):
        """Test data merging functionality."""
        # Prepare data
        self.analyzer.load_data()
        self.analyzer.clean_data()
        
        # Merge data
        merged_data = self.analyzer.merge_data()
        
        # Check structure
        expected_columns = ['article_number', 'price', 'source']
        for col in expected_columns:
            self.assertIn(col, merged_data.columns)
        
        # Check that we have all unique articles
        # Tabelle1: ART001, ART002, ART003, ART004 (ART005 removed due to invalid price)
        # Bestand: ART001, ART002, ART006, ART007 (ART008 removed due to empty price)
        # Total unique: ART001, ART002, ART003, ART004, ART006, ART007
        expected_articles = {'ART001', 'ART002', 'ART003', 'ART004', 'ART006', 'ART007'}
        actual_articles = set(merged_data['article_number'].unique())
        self.assertEqual(actual_articles, expected_articles)
        
        # Check source assignments
        art001_source = merged_data[merged_data['article_number'] == 'ART001']['source'].iloc[0]
        self.assertEqual(art001_source, 'Both (Tabelle1 priority)')
        
        art003_source = merged_data[merged_data['article_number'] == 'ART003']['source'].iloc[0]
        self.assertEqual(art003_source, 'Tabelle1')
        
        art006_source = merged_data[merged_data['article_number'] == 'ART006']['source'].iloc[0]
        self.assertEqual(art006_source, 'Bestand Odoo')

    def test_save_results(self):
        """Test saving results to CSV."""
        # Prepare data
        self.analyzer.load_data()
        self.analyzer.clean_data()
        self.analyzer.merge_data()
        
        # Save results
        output_path = os.path.join(self.temp_dir, "test_output.csv")
        self.analyzer.save_results(output_path)
        
        # Check file was created
        self.assertTrue(os.path.exists(output_path))
        
        # Check file contents
        saved_data = pd.read_csv(output_path)
        self.assertEqual(len(saved_data), len(self.analyzer.merged_data))
        
        # Clean up
        os.remove(output_path)

    def test_save_results_no_merged_data(self):
        """Test saving results when no merged data exists."""
        output_path = os.path.join(self.temp_dir, "test_output.csv")
        
        # Should not raise exception but log error
        self.analyzer.save_results(output_path)
        
        # File should not be created
        self.assertFalse(os.path.exists(output_path))

    def test_save_results_invalid_path(self):
        """Test saving results to invalid path."""
        # Prepare data
        self.analyzer.load_data()
        self.analyzer.clean_data()
        self.analyzer.merge_data()
        
        # Try to save to invalid path
        invalid_path = "/nonexistent_directory/output.csv"
        
        with self.assertRaises(Exception):
            self.analyzer.save_results(invalid_path)

    @patch('builtins.print')
    def test_generate_analytics_report(self, mock_print):
        """Test analytics report generation."""
        # Prepare data
        self.analyzer.load_data()
        self.analyzer.clean_data()
        price_comparison = self.analyzer.analyze_price_differences()
        self.analyzer.merge_data()
        
        # Generate report
        self.analyzer.generate_analytics_report(price_comparison)
        
        # Check that print was called (report was generated)
        self.assertTrue(mock_print.called)
        
        # Check some key report elements were printed
        print_calls = [call[0][0] for call in mock_print.call_args_list if call[0]]
        report_content = ' '.join(str(call) for call in print_calls)
        
        self.assertIn('PURCHASE PRICE ANALYSIS REPORT', report_content)
        self.assertIn('DATA OVERVIEW', report_content)
        self.assertIn('PRICE ANALYSIS', report_content)

    @patch('builtins.print')
    def test_generate_analytics_report_empty_comparison(self, mock_print):
        """Test analytics report with empty price comparison."""
        # Prepare data with no common articles
        self.analyzer.tabelle1_data = pd.DataFrame({
            'article_number': ['ART001'],
            'price': [10.0]
        })
        self.analyzer.bestand_data = pd.DataFrame({
            'article_number': ['ART002'],
            'price': [20.0]
        })
        self.analyzer.merged_data = pd.concat([
            self.analyzer.tabelle1_data.copy(),
            self.analyzer.bestand_data.copy()
        ], ignore_index=True)
        
        # Generate report with empty comparison
        empty_comparison = pd.DataFrame()
        self.analyzer.generate_analytics_report(empty_comparison)
        
        # Should still generate report without price analysis section
        self.assertTrue(mock_print.called)


class TestPriceAnalyzerIntegration(unittest.TestCase):
    """Integration tests for PriceAnalyzer."""

    def setUp(self):
        """Set up integration test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.excel_path = os.path.join(self.temp_dir, "integration_test.xlsx")
        
        # Create realistic test data
        tabelle1_data = pd.DataFrame({
            'Artnr': ['FRAME001', 'LENS002', 'FRAME003', 'LENS004', 'FRAME005'],
            'Fielmann EK': ['125.50€', '89,75', '156.00', '67.25', '198.80'],
            'Description': ['Frame A', 'Lens B', 'Frame C', 'Lens D', 'Frame E']
        })
        
        bestand_data = pd.DataFrame({
            'Interne Referenz': ['FRAME001', 'LENS002', 'CASE006', 'CLEAN007', 'FRAME008'],
            'Kosten': ['120.00', '85,50€', '25.75', '15.00', '175.25'],
            'Category': ['Frame', 'Lens', 'Case', 'Cleaner', 'Frame']
        })
        
        with pd.ExcelWriter(self.excel_path, engine='openpyxl') as writer:
            tabelle1_data.to_excel(writer, sheet_name='Tabelle1', index=False)
            bestand_data.to_excel(writer, sheet_name='Bestand Odoo', index=False)
        
        self.analyzer = PriceAnalyzer(self.excel_path)

    def tearDown(self):
        """Clean up integration test fixtures."""
        if os.path.exists(self.excel_path):
            os.remove(self.excel_path)
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_full_analysis_workflow(self):
        """Test complete analysis workflow."""
        # Run full workflow
        self.analyzer.load_data()
        self.analyzer.clean_data()
        
        common_analysis = self.analyzer.analyze_common_articles()
        price_comparison = self.analyzer.analyze_price_differences()
        merged_data = self.analyzer.merge_data()
        
        # Verify results
        self.assertEqual(common_analysis['common_articles_count'], 2)  # FRAME001, LENS002
        self.assertEqual(len(price_comparison), 2)
        self.assertEqual(len(merged_data), 8)  # All unique articles
        
        # Check price differences are calculated correctly
        frame001_comparison = price_comparison[
            price_comparison['article_number'] == 'FRAME001'
        ].iloc[0]
        self.assertAlmostEqual(frame001_comparison['price_difference'], 5.50, places=2)


if __name__ == '__main__':
    unittest.main()