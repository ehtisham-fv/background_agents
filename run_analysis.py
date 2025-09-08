#!/usr/bin/env python3
"""
Main runner script for the purchase price analysis.
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
sys.path.append(str(Path(__file__).parent / "src"))

from price_analyzer import main

if __name__ == "__main__":
    print("🚀 Starting Purchase Price Analysis...")
    print("=" * 50)
    
    # Check if Excel file exists
    excel_path = "data/purchase_price.xlsx"
    if not os.path.exists(excel_path):
        print(f"❌ Excel file not found: {excel_path}")
        print("📝 Creating sample data for testing...")
        
        # Import and run sample data creation
        from create_sample_data import create_sample_data
        create_sample_data()
        print("✅ Sample data created successfully!")
        print()
    
    # Run the analysis
    try:
        main()
        print("\n✅ Analysis completed successfully!")
        print(f"📊 Results saved to: data/final_purchase_price.csv")
        print(f"📋 Log file: price_analysis.log")
    except Exception as e:
        print(f"❌ Analysis failed: {str(e)}")
        sys.exit(1)
