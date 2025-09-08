# Purchase Price Analyzer - Usage Guide

## Quick Start

1. **Place your Excel file**: Put `purchase_price.xlsx` in the `data/` directory
2. **Run the analysis**: `python3 run_analysis.py`
3. **View results**: Check `data/final_purchase_price.csv`

## File Structure

```
Background_Agents/
├── data/
│   ├── purchase_price.xlsx          # Input Excel file
│   └── final_purchase_price.csv     # Output merged data
├── src/
│   ├── price_analyzer.py            # Main analysis script
│   └── create_sample_data.py        # Sample data generator
├── run_analysis.py                  # Main runner script
├── requirements.txt                 # Python dependencies
└── price_analysis.log              # Analysis log file
```

## Excel File Requirements

Your Excel file must have two sheets:

### Sheet 1: "Tabelle1" (Latest Prices)
- Column `Artnr`: Article numbers
- Column `Fielmann EK`: Purchase prices

### Sheet 2: "Bestand Odoo" (Complete Database)
- Column `Interne Referenz`: Article numbers  
- Column `Kosten`: Purchase prices

## Output

The analysis generates:

1. **CSV File**: `data/final_purchase_price.csv`
   - `article_number`: Standardized article numbers
   - `price`: Purchase price (Tabelle1 takes priority)
   - `source`: Data source (Tabelle1/Bestand Odoo/Both)

2. **Analytics Report**: Console output showing:
   - Common articles count and overlap percentages
   - Price difference statistics
   - Top price increases/decreases
   - Data quality metrics

3. **Log File**: `price_analysis.log` with detailed processing information

## Key Features

- ✅ **Smart Merging**: Tabelle1 prices take priority for common articles
- ✅ **Data Cleaning**: Automatic article number and price standardization
- ✅ **Comprehensive Analytics**: Detailed price comparison and statistics
- ✅ **Error Handling**: Robust error handling and logging
- ✅ **Data Quality**: Identifies duplicates and missing values

## Sample Results

Based on your actual data:
- **Total Articles**: 25,177
- **Common Articles**: 1,789 (95.82% of Tabelle1, 7.13% of Bestand Odoo)
- **Data Sources**: 
  - Tabelle1 only: 1,889 articles
  - Bestand Odoo only: 23,288 articles
  - Common (Tabelle1 priority): 1,789 articles

## Troubleshooting

- **File not found**: Ensure `purchase_price.xlsx` is in the `data/` directory
- **Missing columns**: Check that your Excel sheets have the required column names
- **Installation issues**: Run `python3 -m pip install -r requirements.txt`
- **Logs**: Check `price_analysis.log` for detailed error information
