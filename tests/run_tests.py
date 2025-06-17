#!/usr/bin/env python3
"""
Simple test runner script for Pyferris.

This script provides an easy way to run Pyferris tests with common options.
"""

import sys
import os
import subprocess

def main():
    """Main entry point."""
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Change to the tests directory
    os.chdir(script_dir)
    
    # Check if we're in the right directory
    if not os.path.exists('test_all.py'):
        print("Error: Cannot find test_all.py")
        print("Please run this script from the tests directory")
        return 1
    
    # Parse command line arguments
    if len(sys.argv) == 1:
        # No arguments - run all tests
        print("Running all Pyferris tests...")
        print("Use 'python run_tests.py --help' for more options")
        print()
        return subprocess.call([sys.executable, 'test_all.py'])
    
    elif len(sys.argv) == 2:
        arg = sys.argv[1]
        
        if arg in ['--help', '-h']:
            print_help()
            return 0
        
        elif arg == '--list':
            print_available_modules()
            return 0
        
        elif arg == '--quick':
            print("Running quick test (core functionality only)...")
            return subprocess.call([sys.executable, 'test_all.py', '--module', 'core', '--quiet'])
        
        elif arg == '--io':
            print("Running I/O tests...")
            return subprocess.call([sys.executable, 'test_all.py', '--module', 'simple_io'])
        
        elif arg == '--csv':
            print("Running CSV tests...")
            return subprocess.call([sys.executable, 'test_all.py', '--module', 'csv'])
        
        elif arg == '--json':
            print("Running JSON tests...")
            return subprocess.call([sys.executable, 'test_all.py', '--module', 'json'])
        
        elif arg == '--parallel':
            print("Running parallel I/O tests...")
            return subprocess.call([sys.executable, 'test_all.py', '--module', 'parallel_io'])
        
        elif arg == '--config':
            print("Running configuration tests...")
            return subprocess.call([sys.executable, 'test_all.py', '--module', 'config'])
        
        elif arg == '--executor':
            print("Running executor tests...")
            return subprocess.call([sys.executable, 'test_all.py', '--module', 'executor'])
        
        elif arg == '--verbose':
            print("Running all tests with verbose output...")
            return subprocess.call([sys.executable, 'test_all.py', '-vv'])
        
        elif arg == '--quiet':
            print("Running all tests quietly...")
            return subprocess.call([sys.executable, 'test_all.py', '--quiet'])
        
        else:
            print(f"Unknown option: {arg}")
            print("Use 'python run_tests.py --help' for available options")
            return 1
    
    else:
        # Pass all arguments to test_all.py
        return subprocess.call([sys.executable, 'test_all.py'] + sys.argv[1:])


def print_help():
    """Print help information."""
    print("Pyferris Test Runner")
    print("===================")
    print()
    print("Usage: python run_tests.py [OPTIONS]")
    print()
    print("Options:")
    print("  --help, -h        Show this help message")
    print("  --list            List available test modules")
    print("  --quick           Run quick test (core functionality only)")
    print("  --verbose         Run all tests with verbose output")
    print("  --quiet           Run all tests quietly")
    print()
    print("Module-specific tests:")
    print("  --io              Run I/O tests")
    print("  --csv             Run CSV tests")
    print("  --json            Run JSON tests")
    print("  --parallel        Run parallel I/O tests")
    print("  --config          Run configuration tests")
    print("  --executor        Run executor tests")
    print()
    print("Advanced usage:")
    print("  python run_tests.py --module core --verbose")
    print("  python run_tests.py -vv")
    print("  python run_tests.py --module csv --quiet")
    print()
    print("Examples:")
    print("  python run_tests.py                    # Run all tests")
    print("  python run_tests.py --quick            # Quick test")
    print("  python run_tests.py --csv              # CSV tests only")
    print("  python run_tests.py --verbose          # Verbose output")


def print_available_modules():
    """Print available test modules."""
    print("Available test modules:")
    print("  core        - Core parallel operations (map, filter, reduce, starmap)")
    print("  config      - Configuration management (workers, chunk size)")
    print("  simple_io   - Simple I/O operations (read, write, copy)")
    print("  csv         - CSV file operations (read, write, parse)")
    print("  json        - JSON file operations (read, write, parse)")
    print("  executor    - Executor functionality (task management)")
    print("  parallel_io - Parallel I/O operations (batch processing)")
    print()
    print("Usage: python run_tests.py --module <module_name>")


if __name__ == '__main__':
    sys.exit(main())
