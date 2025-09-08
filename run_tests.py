#!/usr/bin/env python3
"""
Test runner script for the purchase price analysis project.
Provides a single command to run all tests with different options.
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description):
    """Run a command and return the result."""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    return result.returncode == 0


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Run tests for purchase price analysis project")
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument("--integration", action="store_true", help="Run only integration tests")
    parser.add_argument("--coverage", action="store_true", help="Run tests with coverage report")
    parser.add_argument("--html-report", action="store_true", help="Generate HTML coverage report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--fast", action="store_true", help="Skip slow tests")
    parser.add_argument("--file", help="Run tests in specific file")
    
    args = parser.parse_args()
    
    # Base pytest command - try python3 first, then python
    python_cmd = "python3" if subprocess.run(["which", "python3"], capture_output=True).returncode == 0 else "python"
    base_cmd = f"{python_cmd} -m pytest"
    
    # Build command based on arguments
    cmd_parts = [base_cmd]
    
    if args.verbose:
        cmd_parts.append("-v")
    
    if args.coverage:
        cmd_parts.extend(["--cov=src", "--cov-report=term-missing"])
    
    if args.html_report:
        cmd_parts.extend(["--cov=src", "--cov-report=html:htmlcov"])
    
    if args.unit:
        cmd_parts.extend(["-m", "unit"])
    elif args.integration:
        cmd_parts.extend(["-m", "integration"])
    
    if args.fast:
        cmd_parts.extend(["-m", "not slow"])
    
    if args.file:
        cmd_parts.append(f"tests/{args.file}")
    else:
        cmd_parts.append("tests/")
    
    # Join command parts
    cmd = " ".join(cmd_parts)
    
    print("🚀 Purchase Price Analysis - Test Runner")
    print("="*60)
    print(f"Running command: {cmd}")
    
    # Check if pytest is available
    try:
        subprocess.run([python_cmd, "-m", "pytest", "--version"], 
                      check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("❌ pytest not found. Please install pytest:")
        print(f"   System packages: apt install python3-pytest python3-pytest-cov")
        print(f"   Or pip: {python_cmd} -m pip install pytest pytest-cov")
        return 1
    
    # Run the tests
    success = run_command(cmd, "Running Tests")
    
    if success:
        print("\n✅ All tests passed successfully!")
        
        # Show coverage report if requested
        if args.html_report:
            print(f"\n📊 HTML coverage report generated at: {Path.cwd()}/htmlcov/index.html")
        
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1


def run_all_tests():
    """Convenience function to run all tests with coverage."""
    cmd = "python -m pytest tests/ --cov=src --cov-report=term-missing --cov-report=html:htmlcov -v"
    return run_command(cmd, "Running All Tests with Coverage")


def run_unit_tests():
    """Run only unit tests."""
    cmd = "python -m pytest tests/test_price_analyzer.py tests/test_create_sample_data.py -v"
    return run_command(cmd, "Running Unit Tests")


def run_integration_tests():
    """Run only integration tests."""
    cmd = "python -m pytest tests/test_run_analysis.py -v"
    return run_command(cmd, "Running Integration Tests")


if __name__ == "__main__":
    sys.exit(main())