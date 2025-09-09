#!/usr/bin/env python3
"""
Unit tests for the create_sample_data module.
"""

import unittest
import pandas as pd
import tempfile
import os
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from create_sample_data import create_sample_data


class TestCreateSampleData(unittest.TestCase):
    """Test cases for create_sample_data functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.original_cwd = os.getcwd()
        self.temp_dir = tempfile.mkdtemp()
        os.chdir(self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('builtins.print')
    def test_create_sample_data_creates_file(self, mock_print):
        """Test that create_sample_data creates the Excel file."""
        create_sample_data()
        
        # Check that data directory was created
        self.assertTrue(os.path.exists('data'))
        
        # Check that Excel file was created
        self.assertTrue(os.path.exists('data/purchase_price.xlsx'))
        
        # Check that print statements were called
        self.assertTrue(mock_print.called)

    def test_create_sample_data_file_structure(self):
        """Test the structure and content of created Excel file."""
        create_sample_data()
        
        # Read the created Excel file
        excel_path = 'data/purchase_price.xlsx'
        
        # Check Tabelle1 sheet
        tabelle1_df = pd.read_excel(excel_path, sheet_name='Tabelle1')
        self.assertIn('Artnr', tabelle1_df.columns)
        self.assertIn('Fielmann EK', tabelle1_df.columns)
        self.assertIn('Other_Column', tabelle1_df.columns)
        self.assertEqual(len(tabelle1_df), 10)
        
        # Check Bestand Odoo sheet
        bestand_df = pd.read_excel(excel_path, sheet_name='Bestand Odoo')
        self.assertIn('Interne Referenz', bestand_df.columns)
        self.assertIn('Kosten', bestand_df.columns)
        self.assertIn('Other_Column', bestand_df.columns)
        self.assertEqual(len(bestand_df), 13)

    def test_create_sample_data_article_numbers(self):
        """Test that sample data contains expected article numbers."""
        create_sample_data()
        
        excel_path = 'data/purchase_price.xlsx'
        
        # Check Tabelle1 article numbers
        tabelle1_df = pd.read_excel(excel_path, sheet_name='Tabelle1')
        expected_tabelle1_articles = [
            'ART001', 'ART002', 'ART003', 'ART004', 'ART005',
            'ART006', 'ART007', 'ART008', 'ART009', 'ART010'
        ]
        self.assertEqual(list(tabelle1_df['Artnr']), expected_tabelle1_articles)
        
        # Check Bestand Odoo article numbers
        bestand_df = pd.read_excel(excel_path, sheet_name='Bestand Odoo')
        expected_bestand_articles = [
            'ART001', 'ART002', 'ART003', 'ART011', 'ART012',
            'ART013', 'ART014', 'ART015', 'ART016', 'ART017',
            'ART018', 'ART019', 'ART020'
        ]
        self.assertEqual(list(bestand_df['Interne Referenz']), expected_bestand_articles)

    def test_create_sample_data_prices(self):
        """Test that sample data contains expected price values."""
        create_sample_data()
        
        excel_path = 'data/purchase_price.xlsx'
        
        # Check Tabelle1 prices
        tabelle1_df = pd.read_excel(excel_path, sheet_name='Tabelle1')
        expected_tabelle1_prices = [
            15.50, 25.75, 35.00, 45.25, 55.50,
            65.75, 75.00, 85.25, 95.50, 105.75
        ]
        self.assertEqual(list(tabelle1_df['Fielmann EK']), expected_tabelle1_prices)
        
        # Check Bestand Odoo prices
        bestand_df = pd.read_excel(excel_path, sheet_name='Bestand Odoo')
        expected_bestand_prices = [
            14.50, 24.75, 33.00, 50.25, 60.50,
            70.75, 80.00, 90.25, 100.50, 110.75,
            120.00, 130.25, 140.50
        ]
        self.assertEqual(list(bestand_df['Kosten']), expected_bestand_prices)

    def test_create_sample_data_common_articles(self):
        """Test that sample data has expected common articles."""
        create_sample_data()
        
        excel_path = 'data/purchase_price.xlsx'
        
        tabelle1_df = pd.read_excel(excel_path, sheet_name='Tabelle1')
        bestand_df = pd.read_excel(excel_path, sheet_name='Bestand Odoo')
        
        # Find common articles
        tabelle1_articles = set(tabelle1_df['Artnr'])
        bestand_articles = set(bestand_df['Interne Referenz'])
        common_articles = tabelle1_articles.intersection(bestand_articles)
        
        # Should have ART001, ART002, ART003 in common
        expected_common = {'ART001', 'ART002', 'ART003'}
        self.assertEqual(common_articles, expected_common)

    def test_create_sample_data_directory_exists(self):
        """Test behavior when data directory already exists."""
        # Create data directory first
        os.makedirs('data', exist_ok=True)
        
        # Should still work without error
        create_sample_data()
        
        # Check file was still created
        self.assertTrue(os.path.exists('data/purchase_price.xlsx'))

    @patch('builtins.print')
    def test_create_sample_data_output_messages(self, mock_print):
        """Test that create_sample_data prints expected messages."""
        create_sample_data()
        
        # Check that all expected messages were printed
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        
        # Should print file creation message
        file_creation_msg = any("Sample Excel file created" in str(call) for call in print_calls)
        self.assertTrue(file_creation_msg)
        
        # Should print statistics
        tabelle1_msg = any("Tabelle1: 10 articles" in str(call) for call in print_calls)
        self.assertTrue(tabelle1_msg)
        
        bestand_msg = any("Bestand Odoo: 13 articles" in str(call) for call in print_calls)
        self.assertTrue(bestand_msg)
        
        common_msg = any("Common articles: 3" in str(call) for call in print_calls)
        self.assertTrue(common_msg)

    def test_create_sample_data_file_overwrite(self):
        """Test that create_sample_data overwrites existing file."""
        # Create initial file
        os.makedirs('data', exist_ok=True)
        initial_data = pd.DataFrame({'test': [1, 2, 3]})
        initial_data.to_excel('data/purchase_price.xlsx', index=False)
        
        # Run create_sample_data
        create_sample_data()
        
        # Check that file was overwritten with correct structure
        excel_path = 'data/purchase_price.xlsx'
        
        # Should have correct sheets now
        with pd.ExcelFile(excel_path) as xls:
            self.assertIn('Tabelle1', xls.sheet_names)
            self.assertIn('Bestand Odoo', xls.sheet_names)
        
        # Should not have the test column
        tabelle1_df = pd.read_excel(excel_path, sheet_name='Tabelle1')
        self.assertNotIn('test', tabelle1_df.columns)
        self.assertIn('Artnr', tabelle1_df.columns)


class TestCreateSampleDataEdgeCases(unittest.TestCase):
    """Test edge cases for create_sample_data."""

    def setUp(self):
        """Set up test fixtures."""
        self.original_cwd = os.getcwd()
        self.temp_dir = tempfile.mkdtemp()
        os.chdir(self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)


    def test_create_sample_data_data_consistency(self):
        """Test that created data has consistent structure."""
        create_sample_data()
        
        excel_path = 'data/purchase_price.xlsx'
        
        tabelle1_df = pd.read_excel(excel_path, sheet_name='Tabelle1')
        bestand_df = pd.read_excel(excel_path, sheet_name='Bestand Odoo')
        
        # Check data types
        self.assertTrue(pd.api.types.is_object_dtype(tabelle1_df['Artnr']))
        self.assertTrue(pd.api.types.is_numeric_dtype(tabelle1_df['Fielmann EK']))
        
        self.assertTrue(pd.api.types.is_object_dtype(bestand_df['Interne Referenz']))
        self.assertTrue(pd.api.types.is_numeric_dtype(bestand_df['Kosten']))
        
        # Check no null values in key columns
        self.assertFalse(tabelle1_df['Artnr'].isnull().any())
        self.assertFalse(tabelle1_df['Fielmann EK'].isnull().any())
        self.assertFalse(bestand_df['Interne Referenz'].isnull().any())
        self.assertFalse(bestand_df['Kosten'].isnull().any())


if __name__ == '__main__':
    unittest.main()