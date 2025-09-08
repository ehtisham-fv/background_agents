# Purchase Price Analysis Project

A comprehensive Python tool for analyzing and merging purchase price data from Excel sheets, with a complete unit testing suite.

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. Clone the repository and navigate to the project directory
2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Analysis

```bash
# Run the complete analysis
python3 run_analysis.py

# The script will:
# - Create sample data if Excel file doesn't exist
# - Load and clean data from both sheets
# - Analyze price differences
# - Generate merged dataset
# - Save results to CSV
```

## 📁 Project Structure

```
Background_Agents/
├── src/
│   ├── price_analyzer.py      # Main analysis logic
│   └── create_sample_data.py  # Sample data generator
├── tests/
│   ├── test_price_analyzer.py      # Unit tests for PriceAnalyzer
│   ├── test_create_sample_data.py  # Unit tests for sample data
│   └── test_run_analysis.py        # Integration tests
├── data/
│   ├── purchase_price.xlsx    # Input Excel file
│   └── final_purchase_price.csv # Output CSV file
├── run_analysis.py           # Main runner script
├── run_tests.py             # Advanced test runner
├── run_unittest.py          # Simple unittest runner
├── pytest.ini              # Pytest configuration
├── Makefile                 # Build automation
├── TESTING.md              # Detailed testing guide
└── requirements.txt        # Python dependencies
```

## 🧪 Testing

The project includes comprehensive unit tests covering all functionality.

### Quick Test Commands

```bash
# Run all tests with coverage (recommended)
python3 run_tests.py --coverage --html-report

# Simple unittest runner (no external dependencies)
python3 run_unittest.py

# Using make
make test
```

### Test Categories

- **Unit Tests**: Individual component testing
  - `test_price_analyzer.py`: Tests for PriceAnalyzer class
  - `test_create_sample_data.py`: Tests for sample data generation
- **Integration Tests**: End-to-end workflow testing
  - `test_run_analysis.py`: Complete analysis pipeline tests

### Advanced Test Options

```bash
# Run specific test types
python3 run_tests.py --unit          # Unit tests only
python3 run_tests.py --integration   # Integration tests only
python3 run_tests.py --fast          # Skip slow tests

# Run specific test file
python3 run_tests.py --file test_price_analyzer.py

# Generate detailed reports
python3 run_tests.py --html-report   # HTML coverage report
python3 run_tests.py --verbose       # Detailed output
```

### Make Commands

```bash
make help           # Show all available commands
make test           # Run all tests with coverage
make test-unit      # Run unit tests only
make test-integration # Run integration tests only
make test-html      # Generate HTML coverage report
make clean          # Clean up generated files
make run            # Run the price analysis
```

## 📊 Features

### Data Processing
- ✅ Load data from multiple Excel sheets
- ✅ Clean and standardize article numbers
- ✅ Parse and convert price formats (€, $, commas)
- ✅ Handle missing and invalid data
- ✅ Remove duplicates and empty entries

### Analysis
- ✅ Find common articles between datasets
- ✅ Calculate price differences and percentages
- ✅ Generate overlap statistics
- ✅ Merge data with priority rules

### Output
- ✅ Save merged data to CSV
- ✅ Generate detailed analytics report
- ✅ Create comprehensive logs
- ✅ Display progress and statistics

### Testing
- ✅ 100% test coverage of core functionality
- ✅ Unit tests for all classes and methods
- ✅ Integration tests for complete workflows
- ✅ Edge case and error handling tests
- ✅ Multiple test runners (pytest, unittest)
- ✅ HTML coverage reports
- ✅ Continuous integration ready

## 🔧 Configuration

### Input Data Format

The tool expects an Excel file with two sheets:

**Tabelle1 Sheet:**
- `Artnr`: Article number
- `Fielmann EK`: Purchase price

**Bestand Odoo Sheet:**
- `Interne Referenz`: Article number
- `Kosten`: Cost price

### Output Format

The merged CSV file contains:
- `article_number`: Standardized article identifier
- `price`: Cleaned price value
- `source`: Data source ("Tabelle1", "Bestand Odoo", or "Both (Tabelle1 priority)")

## 🧪 Test Coverage

Current test coverage includes:

### PriceAnalyzer Tests (test_price_analyzer.py)
- ✅ Initialization and configuration
- ✅ Data loading from Excel files
- ✅ Error handling for missing files
- ✅ Data cleaning and standardization
- ✅ Price format conversion
- ✅ Common article analysis
- ✅ Price difference calculations
- ✅ Data merging with priority rules
- ✅ CSV output generation
- ✅ Analytics report generation
- ✅ Integration workflow tests

### Sample Data Tests (test_create_sample_data.py)
- ✅ Excel file creation
- ✅ Data structure validation
- ✅ Article number generation
- ✅ Price value validation
- ✅ Common article verification
- ✅ File overwrite behavior
- ✅ Error handling

### Integration Tests (test_run_analysis.py)
- ✅ Complete analysis workflow
- ✅ File handling and creation
- ✅ Command-line execution
- ✅ Error scenario handling
- ✅ Log file generation
- ✅ Output file validation

## 📈 Usage Examples

### Basic Usage

```python
from src.price_analyzer import PriceAnalyzer

# Initialize analyzer
analyzer = PriceAnalyzer("data/purchase_price.xlsx")

# Load and process data
analyzer.load_data()
analyzer.clean_data()

# Analyze and merge
common_analysis = analyzer.analyze_common_articles()
price_comparison = analyzer.analyze_price_differences()
merged_data = analyzer.merge_data()

# Save results
analyzer.save_results("output/final_prices.csv")
analyzer.generate_analytics_report(price_comparison)
```

### Test Development

```python
import unittest
from src.price_analyzer import PriceAnalyzer

class TestNewFeature(unittest.TestCase):
    def setUp(self):
        # Set up test fixtures
        pass
    
    def test_new_functionality(self):
        # Test implementation
        pass
```

## 🛠️ Development

### Adding New Tests

1. Create test file in `tests/` directory
2. Follow naming convention: `test_*.py`
3. Use descriptive test method names
4. Include setup and teardown methods
5. Test edge cases and error conditions

### Running Development Tests

```bash
# Run tests during development
python3 run_tests.py --verbose

# Run specific test during development
python3 -m unittest tests.test_price_analyzer.TestPriceAnalyzer.test_load_data_success

# Generate coverage report
python3 run_tests.py --coverage --html-report
```

## 📋 Dependencies

### Core Dependencies
- `pandas>=1.5.0`: Data manipulation and analysis
- `openpyxl>=3.0.0`: Excel file reading/writing
- `numpy>=1.21.0`: Numerical computations

### Testing Dependencies
- `pytest>=7.0.0`: Advanced testing framework
- `pytest-cov>=4.0.0`: Coverage reporting

### Optional Development Dependencies
- `flake8`: Code linting
- `black`: Code formatting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all tests pass: `make test`
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 📞 Support

For questions or issues:
1. Check the [TESTING.md](TESTING.md) documentation
2. Run the test suite to verify your setup
3. Open an issue with detailed information

## 🔄 Recent Updates

- ✅ Complete unit test suite with 80%+ coverage
- ✅ Multiple test runners (pytest, unittest, make)
- ✅ HTML coverage reporting
- ✅ Integration tests for complete workflows
- ✅ Comprehensive error handling tests
- ✅ CI/CD ready test configuration