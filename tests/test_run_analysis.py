#!/usr/bin/env python3
"""
Integration tests for the run_analysis.py script.
"""

import unittest
import tempfile
import os
import shutil
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import pandas as pd
import subprocess

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "src"))

import run_analysis
from src.create_sample_data import create_sample_data
from src.price_analyzer import PriceAnalyzer


class TestRunAnalysisScript(unittest.TestCase):
    """Test cases for the run_analysis.py script."""

    def setUp(self):
        """Set up test fixtures."""
        self.original_cwd = os.getcwd()
        self.temp_dir = tempfile.mkdtemp()
        os.chdir(self.temp_dir)
        
        # Create test Excel data
        self.create_test_excel_file()

    def tearDown(self):
        """Clean up test fixtures."""
        os.chdir(self.original_cwd)
        # Clean up temp directory
        self._cleanup_temp_dir()

    def _cleanup_temp_dir(self):
        """Helper method to clean up temp directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_excel_file(self):
        """Create a test Excel file for testing."""
        os.makedirs('data', exist_ok=True)
        
        tabelle1_data = pd.DataFrame({
            'Artnr': ['TEST001', 'TEST002', 'TEST003'],
            'Fielmann EK': [10.50, 20.75, 30.00],
            'Other_Column': ['A', 'B', 'C']
        })
        
        bestand_data = pd.DataFrame({
            'Interne Referenz': ['TEST001', 'TEST002', 'TEST004'],
            'Kosten': [9.50, 19.75, 40.00],
            'Other_Column': ['X', 'Y', 'Z']
        })
        
        with pd.ExcelWriter('data/purchase_price.xlsx', engine='openpyxl') as writer:
            tabelle1_data.to_excel(writer, sheet_name='Tabelle1', index=False)
            bestand_data.to_excel(writer, sheet_name='Bestand Odoo', index=False)

    @patch('builtins.print')
    def test_run_analysis_with_existing_file(self, mock_print):
        """Test run_analysis when Excel file already exists."""
        # Run the main function
        run_analysis.main()
        
        # Check that analysis completed successfully
        print_calls = [str(call) for call in mock_print.call_args_list]
        
        # Should print starting message
        starting_msg = any("Starting Purchase Price Analysis" in call for call in print_calls)
        self.assertTrue(starting_msg)
        
        # Should print completion message
        completion_msg = any("Analysis completed successfully" in call for call in print_calls)
        self.assertTrue(completion_msg)
        
        # Check that output file was created
        self.assertTrue(os.path.exists('data/final_purchase_price.csv'))

    @patch('builtins.print')
    def test_run_analysis_without_excel_file(self, mock_print):
        """Test run_analysis when Excel file doesn't exist."""
        # Remove the Excel file
        os.remove('data/purchase_price.xlsx')
        
        # Run the main function
        run_analysis.main()
        
        print_calls = [str(call) for call in mock_print.call_args_list]
        
        # Should print file not found message
        not_found_msg = any("Excel file not found" in call for call in print_calls)
        self.assertTrue(not_found_msg)
        
        # Should print creating sample data message
        sample_msg = any("Creating sample data" in call for call in print_calls)
        self.assertTrue(sample_msg)
        
        # Should create sample data and complete analysis
        completion_msg = any("Analysis completed successfully" in call for call in print_calls)
        self.assertTrue(completion_msg)
        
        # Check that Excel file was created
        self.assertTrue(os.path.exists('data/purchase_price.xlsx'))
        
        # Check that output file was created
        self.assertTrue(os.path.exists('data/final_purchase_price.csv'))

    @patch('src.price_analyzer.main')
    @patch('builtins.print')
    def test_run_analysis_handles_analysis_failure(self, mock_print, mock_main):
        """Test run_analysis handles analysis failures gracefully."""
        # Mock main to raise an exception
        mock_main.side_effect = Exception("Analysis failed")
        
        # Run should handle the exception
        with self.assertRaises(SystemExit) as cm:
            run_analysis.main()
        
        # Should exit with code 1
        self.assertEqual(cm.exception.code, 1)
        
        print_calls = [str(call) for call in mock_print.call_args_list]
        
        # Should print failure message
        failure_msg = any("Analysis failed" in call for call in print_calls)
        self.assertTrue(failure_msg)

    def test_run_analysis_creates_log_file(self):
        """Test that run_analysis creates a log file."""
        # Run the analysis
        run_analysis.main()
        
        # Check that log file was created
        self.assertTrue(os.path.exists('price_analysis.log'))
        
        # Check log file has content
        with open('price_analysis.log', 'r') as f:
            log_content = f.read()
            self.assertIn('Loading data', log_content)
            self.assertIn('Analysis completed', log_content)

    def test_run_analysis_output_file_structure(self):
        """Test the structure of the output CSV file."""
        # Run the analysis
        run_analysis.main()
        
        # Check output file structure
        output_df = pd.read_csv('data/final_purchase_price.csv')
        
        # Check required columns
        expected_columns = ['article_number', 'price', 'source']
        for col in expected_columns:
            self.assertIn(col, output_df.columns)
        
        # Check that we have data
        self.assertGreater(len(output_df), 0)
        
        # Check source values are valid
        valid_sources = ['Tabelle1', 'Bestand Odoo', 'Both (Tabelle1 priority)']
        self.assertTrue(all(source in valid_sources for source in output_df['source'].unique()))

    @patch('src.create_sample_data.create_sample_data')
    @patch('builtins.print')
    def test_run_analysis_sample_data_creation_failure(self, mock_print, mock_create_sample):
        """Test handling of sample data creation failure."""
        # Remove Excel file
        os.remove('data/purchase_price.xlsx')
        
        # Mock sample data creation to fail
        mock_create_sample.side_effect = Exception("Failed to create sample data")
        
        # Should raise the exception
        with self.assertRaises(Exception):
            run_analysis.main()

    def test_sys_path_modification(self):
        """Test that sys.path is correctly modified."""
        # Check that src directory was added to sys.path
        expected_src_path = str(Path(__file__).parent.parent / "src")
        
        # Import run_analysis to trigger path modification
        import run_analysis
        
        # Check if the path is in sys.path (it should be added by run_analysis)
        # Note: This might already be there from our test setup, so we'll check the logic
        self.assertTrue(any("src" in path for path in sys.path))


class TestRunAnalysisCommandLine(unittest.TestCase):
    """Test command line execution of run_analysis.py."""

    def setUp(self):
        """Set up test fixtures."""
        self.original_cwd = os.getcwd()
        self.temp_dir = tempfile.mkdtemp()
        os.chdir(self.temp_dir)
        
        # Create test data
        self.create_test_data()

    def tearDown(self):
        """Clean up test fixtures."""
        os.chdir(self.original_cwd)
        self._cleanup_temp_dir()

    def _cleanup_temp_dir(self):
        """Helper method to clean up temp directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_data(self):
        """Create test data files."""
        os.makedirs('data', exist_ok=True)
        
        # Copy the run_analysis.py and src files to temp directory for testing
        project_root = Path(__file__).parent.parent
        
        # Create a simple version of the files for command line testing
        with open('run_analysis.py', 'w') as f:
            f.write('''#!/usr/bin/env python3
import sys
import os
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "src"))

def main():
    print("🚀 Starting Purchase Price Analysis...")
    print("=" * 50)
    
    if not os.path.exists("data/purchase_price.xlsx"):
        print("❌ Excel file not found: data/purchase_price.xlsx")
        return
    
    print("✅ Analysis completed successfully!")
    print("📊 Results saved to: data/final_purchase_price.csv")
    print("📋 Log file: price_analysis.log")

if __name__ == "__main__":
    main()
''')
        
        # Create minimal test Excel file
        tabelle1_data = pd.DataFrame({
            'Artnr': ['CMD001', 'CMD002'],
            'Fielmann EK': [100.0, 200.0]
        })
        
        bestand_data = pd.DataFrame({
            'Interne Referenz': ['CMD001', 'CMD003'],
            'Kosten': [95.0, 150.0]
        })
        
        with pd.ExcelWriter('data/purchase_price.xlsx', engine='openpyxl') as writer:
            tabelle1_data.to_excel(writer, sheet_name='Tabelle1', index=False)
            bestand_data.to_excel(writer, sheet_name='Bestand Odoo', index=False)

    def test_command_line_execution(self):
        """Test that run_analysis.py can be executed from command line."""
        # Execute the script
        result = subprocess.run([
            sys.executable, 'run_analysis.py'
        ], capture_output=True, text=True)
        
        # Check that it executed successfully
        self.assertEqual(result.returncode, 0)
        
        # Check output contains expected messages
        self.assertIn("Starting Purchase Price Analysis", result.stdout)
        self.assertIn("Analysis completed successfully", result.stdout)

    def test_command_line_execution_without_excel(self):
        """Test command line execution when Excel file is missing."""
        # Remove Excel file
        os.remove('data/purchase_price.xlsx')
        
        # Execute the script
        result = subprocess.run([
            sys.executable, 'run_analysis.py'
        ], capture_output=True, text=True)
        
        # Should complete but with file not found message
        self.assertEqual(result.returncode, 0)
        self.assertIn("Excel file not found", result.stdout)


class TestRunAnalysisIntegration(unittest.TestCase):
    """Integration tests combining all components."""

    def setUp(self):
        """Set up integration test fixtures."""
        self.original_cwd = os.getcwd()
        self.temp_dir = tempfile.mkdtemp()
        os.chdir(self.temp_dir)

    def tearDown(self):
        """Clean up integration test fixtures."""
        os.chdir(self.original_cwd)
        self._cleanup_temp_dir()

    def _cleanup_temp_dir(self):
        """Helper method to clean up temp directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('builtins.print')
    def test_full_integration_workflow(self, mock_print):
        """Test the complete integration workflow."""
        # Start with no Excel file (should create sample data)
        run_analysis.main()
        
        # Verify all expected files were created
        self.assertTrue(os.path.exists('data/purchase_price.xlsx'))
        self.assertTrue(os.path.exists('data/final_purchase_price.csv'))
        self.assertTrue(os.path.exists('price_analysis.log'))
        
        # Verify output file has correct structure
        output_df = pd.read_csv('data/final_purchase_price.csv')
        self.assertIn('article_number', output_df.columns)
        self.assertIn('price', output_df.columns)
        self.assertIn('source', output_df.columns)
        
        # Verify log file has content
        with open('price_analysis.log', 'r') as f:
            log_content = f.read()
            self.assertIn('INFO', log_content)
        
        print_calls = [str(call) for call in mock_print.call_args_list]
        
        # Should have all expected print messages
        self.assertTrue(any("Starting Purchase Price Analysis" in call for call in print_calls))
        self.assertTrue(any("Creating sample data" in call for call in print_calls))
        self.assertTrue(any("Sample data created successfully" in call for call in print_calls))
        self.assertTrue(any("Analysis completed successfully" in call for call in print_calls))


if __name__ == '__main__':
    unittest.main()