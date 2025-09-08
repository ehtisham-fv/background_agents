#!/usr/bin/env python3
"""
Create sample Excel data for testing the price analyzer.
"""

import pandas as pd
import numpy as np
from pathlib import Path

def create_sample_data():
    """Create sample Excel data with two sheets."""
    
    # Create data directory if it doesn't exist
    Path("data").mkdir(exist_ok=True)
    
    # Sample data for Tabelle1 (latest prices)
    tabelle1_data = {
        'Artnr': [
            'ART001', 'ART002', 'ART003', 'ART004', 'ART005',
            'ART006', 'ART007', 'ART008', 'ART009', 'ART010'
        ],
        'Fielmann EK': [
            15.50, 25.75, 35.00, 45.25, 55.50,
            65.75, 75.00, 85.25, 95.50, 105.75
        ],
        'Other_Column': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    }
    
    # Sample data for Bestand Odoo (complete database)
    bestand_data = {
        'Interne Referenz': [
            'ART001', 'ART002', 'ART003', 'ART011', 'ART012',
            'ART013', 'ART014', 'ART015', 'ART016', 'ART017',
            'ART018', 'ART019', 'ART020'
        ],
        'Kosten': [
            14.50, 24.75, 33.00, 50.25, 60.50,
            70.75, 80.00, 90.25, 100.50, 110.75,
            120.00, 130.25, 140.50
        ],
        'Other_Column': ['X', 'Y', 'Z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    }
    
    # Create DataFrames
    df_tabelle1 = pd.DataFrame(tabelle1_data)
    df_bestand = pd.DataFrame(bestand_data)
    
    # Create Excel file with multiple sheets
    with pd.ExcelWriter('data/purchase_price.xlsx', engine='openpyxl') as writer:
        df_tabelle1.to_excel(writer, sheet_name='Tabelle1', index=False)
        df_bestand.to_excel(writer, sheet_name='Bestand Odoo', index=False)
    
    print("Sample Excel file created: data/purchase_price.xlsx")
    print(f"Tabelle1: {len(df_tabelle1)} articles")
    print(f"Bestand Odoo: {len(df_bestand)} articles")
    print(f"Common articles: {len(set(df_tabelle1['Artnr']).intersection(set(df_bestand['Interne Referenz'])))}")

if __name__ == "__main__":
    create_sample_data()
