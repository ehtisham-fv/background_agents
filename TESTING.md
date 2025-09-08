# Testing Guide for Purchase Price Analysis

This document describes how to run and work with the test suite for the Purchase Price Analysis project.

## Quick Start

### Single Command to Run All Tests
```bash
# Run all tests with coverage
python run_tests.py --coverage --html-report

# Or using make
make test
```

## Test Structure

The test suite is organized as follows:

```
tests/
├── __init__.py
├── test_price_analyzer.py      # Unit tests for PriceAnalyzer class
├── test_create_sample_data.py  # Unit tests for sample data creation
└── test_run_analysis.py        # Integration tests for main script
```

## Running Tests

### Using the Test Runner Script

The `run_tests.py` script provides various options:

```bash
# Run all tests
python run_tests.py

# Run with coverage report
python run_tests.py --coverage

# Run with HTML coverage report
python run_tests.py --html-report

# Run only unit tests
python run_tests.py --unit

# Run only integration tests
python run_tests.py --integration

# Run tests in verbose mode
python run_tests.py --verbose

# Run fast tests only (skip slow ones)
python run_tests.py --fast

# Run specific test file
python run_tests.py --file test_price_analyzer.py
```

### Using pytest directly

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=term-missing

# Run specific test file
python -m pytest tests/test_price_analyzer.py

# Run specific test method
python -m pytest tests/test_price_analyzer.py::TestPriceAnalyzer::test_load_data_success

# Run with verbose output
python -m pytest tests/ -v
```

### Using Make

```bash
# Run all tests with coverage
make test

# Run only unit tests
make test-unit

# Run only integration tests
make test-integration

# Run with HTML coverage report
make test-html

# Run specific test file
make test-file FILE=test_price_analyzer.py
```

## Test Categories

### Unit Tests

Unit tests focus on individual components:

- **`test_price_analyzer.py`**: Tests for the `PriceAnalyzer` class
  - Data loading and validation
  - Data cleaning and transformation
  - Price analysis and comparison
  - Data merging logic
  - Error handling

- **`test_create_sample_data.py`**: Tests for sample data generation
  - Excel file creation
  - Data structure validation
  - Error handling

### Integration Tests

Integration tests verify the complete workflow:

- **`test_run_analysis.py`**: Tests for the main analysis script
  - End-to-end workflow
  - File handling
  - Command-line execution
  - Error scenarios

## Test Coverage

The test suite aims for high coverage of the source code:

- **Target**: 80% minimum coverage
- **Current coverage**: View with `python run_tests.py --coverage`
- **HTML report**: Generate with `python run_tests.py --html-report`

### Coverage Reports

After running tests with coverage, you can view:

1. **Terminal report**: Shows coverage percentages and missing lines
2. **HTML report**: Detailed interactive report at `htmlcov/index.html`

## Writing New Tests

### Test File Naming

- Test files should start with `test_`
- Test classes should start with `Test`
- Test methods should start with `test_`

### Test Structure

```python
import unittest
import tempfile
import os
from pathlib import Path

class TestNewFeature(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create temporary directories/files
        pass
    
    def tearDown(self):
        """Clean up after each test method."""
        # Remove temporary files
        pass
    
    def test_feature_functionality(self):
        """Test the main functionality."""
        # Arrange
        # Act
        # Assert
        pass
```

### Best Practices

1. **Use descriptive test names**: `test_load_data_with_missing_file`
2. **Follow AAA pattern**: Arrange, Act, Assert
3. **Test edge cases**: Empty data, invalid input, etc.
4. **Use temporary files**: Don't modify real project files
5. **Mock external dependencies**: Use `unittest.mock` for external calls
6. **Clean up resources**: Always clean up temporary files/directories

## Continuous Integration

The test suite is designed to work in CI environments:

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
python run_tests.py --coverage

# Check exit code
echo $?
```

## Debugging Tests

### Running Individual Tests

```bash
# Run single test method
python -m pytest tests/test_price_analyzer.py::TestPriceAnalyzer::test_load_data_success -v

# Run with debugging output
python -m pytest tests/test_price_analyzer.py -v -s

# Stop on first failure
python -m pytest tests/ -x
```

### Using Python Debugger

```python
import pdb; pdb.set_trace()  # Add this line in your test
```

### Test Output

- Use `print()` statements for debugging (with `-s` flag)
- Check temporary file contents
- Verify mock call arguments

## Common Issues

### Import Errors

Make sure the project structure is correct:
```bash
# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Check if modules can be imported
python -c "from src.price_analyzer import PriceAnalyzer"
```

### File Permission Errors

Tests create temporary files. Ensure:
- Write permissions in test directory
- Proper cleanup in `tearDown()` methods

### Mock Issues

When using mocks:
- Verify the correct import path
- Check mock call arguments
- Reset mocks between tests

## Performance

### Test Execution Time

Monitor test performance:
```bash
# Show slowest tests
python -m pytest tests/ --durations=10
```

### Optimizing Slow Tests

- Use smaller test data sets
- Mock expensive operations
- Mark slow tests with `@pytest.mark.slow`

## Dependencies

Test dependencies are listed in `requirements.txt`:
- `pytest>=7.0.0`: Test framework
- `pytest-cov>=4.0.0`: Coverage reporting

Optional dependencies for enhanced testing:
```bash
pip install flake8  # Code linting
pip install black   # Code formatting
```