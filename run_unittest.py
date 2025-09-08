#!/usr/bin/env python3
"""
Simple unittest runner for the purchase price analysis project.
Works with Python's built-in unittest module without external dependencies.
"""

import unittest
import sys
import os
from pathlib import Path


def run_tests():
    """Run all unit tests using Python's built-in unittest."""
    print("🚀 Purchase Price Analysis - Unit Test Runner")
    print("="*60)
    
    # Add project root to Python path
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    # Discover and run tests
    loader = unittest.TestLoader()
    
    try:
        # Try to load tests from the tests directory
        suite = loader.discover('tests', pattern='test_*.py')
        
        # Run the tests
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        # Print summary
        print("\n" + "="*60)
        if result.wasSuccessful():
            print(f"✅ All tests passed! ({result.testsRun} tests)")
            return 0
        else:
            print(f"❌ Tests failed! ({len(result.failures)} failures, {len(result.errors)} errors)")
            return 1
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\n💡 Make sure you have installed the required dependencies:")
        print("   pip install -r requirements.txt")
        print("\n   Or install system packages:")
        print("   apt install python3-pandas python3-openpyxl python3-numpy")
        return 1
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1


def main():
    """Main function."""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Usage: python3 run_unittest.py")
        print("Runs all unit tests using Python's built-in unittest module.")
        return 0
    
    return run_tests()


if __name__ == "__main__":
    sys.exit(main())