# Implementation Plan: Excel Purchase Price Analysis and Merging

## Project Overview
Analyze two Excel sheets containing article numbers and purchase prices, merge the data, and generate analytics.

## Data Sources
- **File**: `data/purchase_price.xlsx`
- **Sheet 1**: `Tabelle1` - Latest prices (2024)
  - Article Number: `Artnr` column
  - Price: `Fielmann EK` column
- **Sheet 2**: `Bestand Odoo` - Complete article database
  - Article Number: `Interne Referenz` column
  - Price: `Kosten` column

## Implementation Steps

### 1. Environment Setup
- Create `data/` directory structure
- Install required Python packages: `pandas`, `openpyxl`
- Create `requirements.txt` for dependency management

### 2. Data Loading and Preprocessing
- Load both Excel sheets using pandas
- Clean and standardize article numbers (remove whitespace, convert to string)
- Clean price data (remove currency symbols, convert to numeric)
- Handle missing values appropriately

### 3. Data Analysis
- **Common Articles Analysis**:
  - Find intersection of article numbers between both sheets
  - Count and report common articles
  - Calculate overlap percentage

- **Price Comparison Analysis**:
  - Compare prices for common articles
  - Calculate price differences (absolute and percentage)
  - Identify articles with significant price changes
  - Generate statistics (mean, median, std deviation of price differences)

### 4. Data Merging Strategy
- **Priority**: Tabelle1 prices (most recent) take precedence
- **Merge Logic**:
  - If article exists in both sheets → use Tabelle1 price
  - If article exists only in Bestand Odoo → use Bestand Odoo price
  - If article exists only in Tabelle1 → use Tabelle1 price

### 5. Output Generation
- **Final Dataset**: `data/final_purchase_price.csv`
- **Columns**: Article Number, Price, Source (Tabelle1/Bestand Odoo/Both)
- **Analytics Report**: Generate summary statistics and insights

### 6. Analytics and Reporting
- Total number of articles in each sheet
- Number of common articles
- Price difference statistics
- Articles with largest price increases/decreases
- Data quality metrics (missing values, duplicates)

## Technical Requirements
- Python 3.7+
- pandas for data manipulation
- openpyxl for Excel file reading
- Error handling for file operations
- Logging for debugging and monitoring

## File Structure
```
Background_Agents/
├── data/
│   ├── purchase_price.xlsx
│   └── final_purchase_price.csv
├── src/
│   └── price_analyzer.py
├── requirements.txt
├── implementation_plan.md
└── README.md
```

## Expected Outputs
1. **Console Output**: Analysis summary and statistics
2. **CSV File**: Merged purchase price data
3. **Log File**: Processing details and any warnings/errors
4. **Analytics Report**: Detailed insights and recommendations

## Error Handling
- File not found errors
- Invalid Excel format
- Missing columns
- Data type conversion errors
- Empty sheets or invalid data

## Future Enhancements
- Data validation rules
- Price trend analysis over time
- Automated report generation
- Integration with external systems
- Data visualization capabilities
