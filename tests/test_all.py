"""
Comprehensive test runner for all Pyferris features.

This module runs all test suites and provides a comprehensive summary
of test results across all components.
"""

import unittest
import sys
import time
from io import StringIO

# Import all test modules
import test_core
import test_config
import test_simple_io
import test_csv
import test_json
import test_executor
import test_parallel_io


class PyferrisTestRunner:
    """Custom test runner for Pyferris test suite."""
    
    def __init__(self):
        self.test_modules = [
            ('Core Parallel Operations', test_core),
            ('Configuration Management', test_config),
            ('Simple I/O Operations', test_simple_io),
            ('CSV I/O Operations', test_csv),
            ('JSON I/O Operations', test_json),
            ('Executor Functionality', test_executor),
            ('Parallel I/O Operations', test_parallel_io),
        ]
        
        self.results = {}
        self.total_tests = 0
        self.total_failures = 0
        self.total_errors = 0
        self.total_time = 0
    
    def run_all_tests(self, verbosity=2):
        """Run all test suites and collect results."""
        print("=" * 80)
        print("PYFERRIS COMPREHENSIVE TEST SUITE")
        print("=" * 80)
        print()
        
        overall_start_time = time.time()
        
        for module_name, test_module in self.test_modules:
            print(f"Running {module_name} Tests...")
            print("-" * 60)
            
            # Capture output
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            stdout_capture = StringIO()
            stderr_capture = StringIO()
            
            try:
                # Redirect output during test execution
                if verbosity < 2:
                    sys.stdout = stdout_capture
                    sys.stderr = stderr_capture
                
                # Create test suite for this module
                loader = unittest.TestLoader()
                suite = loader.loadTestsFromModule(test_module)
                
                # Run tests
                start_time = time.time()
                runner = unittest.TextTestRunner(
                    verbosity=verbosity,
                    stream=sys.stdout,
                    buffer=True
                )
                result = runner.run(suite)
                end_time = time.time()
                
                # Store results
                self.results[module_name] = {
                    'tests_run': result.testsRun,
                    'failures': len(result.failures),
                    'errors': len(result.errors),
                    'time': end_time - start_time,
                    'success_rate': ((result.testsRun - len(result.failures) - len(result.errors)) / max(result.testsRun, 1)) * 100,
                    'failure_details': result.failures,
                    'error_details': result.errors
                }
                
                # Update totals
                self.total_tests += result.testsRun
                self.total_failures += len(result.failures)
                self.total_errors += len(result.errors)
                
                # Print module summary
                print(f"\n{module_name} Results:")
                print(f"  Tests run: {result.testsRun}")
                print(f"  Failures: {len(result.failures)}")
                print(f"  Errors: {len(result.errors)}")
                print(f"  Success rate: {self.results[module_name]['success_rate']:.1f}%")
                print(f"  Time: {end_time - start_time:.3f}s")
                print()
                
            except Exception as e:
                print(f"ERROR: Failed to run {module_name} tests: {e}")
                self.results[module_name] = {
                    'tests_run': 0,
                    'failures': 0,
                    'errors': 1,
                    'time': 0,
                    'success_rate': 0,
                    'failure_details': [],
                    'error_details': [(f"{module_name} module", str(e))]
                }
                self.total_errors += 1
                
            finally:
                # Restore output
                sys.stdout = old_stdout
                sys.stderr = old_stderr
        
        overall_end_time = time.time()
        self.total_time = overall_end_time - overall_start_time
        
        # Print comprehensive summary
        self.print_summary()
        
        return self.get_exit_code()
    
    def print_summary(self):
        """Print comprehensive test summary."""
        print("=" * 80)
        print("COMPREHENSIVE TEST SUMMARY")
        print("=" * 80)
        print()
        
        # Overall statistics
        overall_success_rate = ((self.total_tests - self.total_failures - self.total_errors) / max(self.total_tests, 1)) * 100
        
        print("Overall Results:")
        print(f"  Total tests run: {self.total_tests}")
        print(f"  Total failures: {self.total_failures}")
        print(f"  Total errors: {self.total_errors}")
        print(f"  Overall success rate: {overall_success_rate:.1f}%")
        print(f"  Total execution time: {self.total_time:.3f}s")
        print()
        
        # Module breakdown
        print("Module Breakdown:")
        print(f"{'Module':<30} {'Tests':<8} {'Failures':<10} {'Errors':<8} {'Success %':<10} {'Time (s)':<10}")
        print("-" * 80)
        
        for module_name, results in self.results.items():
            print(f"{module_name:<30} {results['tests_run']:<8} {results['failures']:<10} "
                  f"{results['errors']:<8} {results['success_rate']:<10.1f} {results['time']:<10.3f}")
        
        print()
        
        # Detailed failure and error reporting
        if self.total_failures > 0 or self.total_errors > 0:
            print("=" * 80)
            print("DETAILED FAILURE AND ERROR REPORT")
            print("=" * 80)
            
            for module_name, results in self.results.items():
                if results['failures'] or results['errors']:
                    print(f"\n{module_name}:")
                    print("-" * 40)
                    
                    if results['failures']:
                        print("FAILURES:")
                        for test, traceback in results['failure_details']:
                            print(f"  - {test}")
                            # Print first few lines of traceback
                            traceback_lines = str(traceback).split('\n')[:3]
                            for line in traceback_lines:
                                if line.strip():
                                    print(f"    {line.strip()}")
                            print()
                    
                    if results['errors']:
                        print("ERRORS:")
                        for test, traceback in results['error_details']:
                            print(f"  - {test}")
                            # Print first few lines of traceback
                            traceback_lines = str(traceback).split('\n')[:3]
                            for line in traceback_lines:
                                if line.strip():
                                    print(f"    {line.strip()}")
                            print()
        
        # Performance summary
        print("=" * 80)
        print("PERFORMANCE SUMMARY")
        print("=" * 80)
        
        # Sort modules by execution time
        sorted_modules = sorted(self.results.items(), key=lambda x: x[1]['time'], reverse=True)
        
        print("Modules by execution time:")
        for module_name, results in sorted_modules:
            if results['tests_run'] > 0:
                avg_time = results['time'] / results['tests_run']
                print(f"  {module_name}: {results['time']:.3f}s total, {avg_time:.4f}s per test")
        
        print()
        
        # Recommendations
        print("=" * 80)
        print("RECOMMENDATIONS")
        print("=" * 80)
        
        if overall_success_rate == 100:
            print("🎉 Excellent! All tests passed successfully.")
            print("   Your Pyferris installation is working perfectly.")
        elif overall_success_rate >= 90:
            print("✅ Good! Most tests passed successfully.")
            print("   There are a few issues to address, but core functionality works.")
        elif overall_success_rate >= 70:
            print("⚠️  Warning! Some significant issues were found.")
            print("   Review the failures and errors above.")
        else:
            print("❌ Critical! Many tests failed.")
            print("   There may be installation or compatibility issues.")
        
        print()
        
        # Specific recommendations based on results
        failing_modules = [name for name, results in self.results.items() 
                          if results['success_rate'] < 100]
        
        if failing_modules:
            print("Modules with issues:")
            for module in failing_modules:
                results = self.results[module]
                print(f"  - {module}: {results['success_rate']:.1f}% success rate")
            
            print("\nTroubleshooting tips:")
            print("  1. Ensure all dependencies are installed")
            print("  2. Check that the Rust extension is compiled correctly")
            print("  3. Verify file permissions for I/O operations")
            print("  4. Check system resources (memory, disk space)")
        
        print()
    
    def get_exit_code(self):
        """Get appropriate exit code based on test results."""
        if self.total_failures == 0 and self.total_errors == 0:
            return 0  # Success
        else:
            return 1  # Failure


def run_specific_module(module_name, verbosity=2):
    """Run tests for a specific module."""
    module_map = {
        'core': test_core,
        'config': test_config,
        'simple_io': test_simple_io,
        'csv': test_csv,
        'json': test_json,
        'executor': test_executor,
        'parallel_io': test_parallel_io,
    }
    
    if module_name not in module_map:
        print(f"Unknown module: {module_name}")
        print(f"Available modules: {', '.join(module_map.keys())}")
        return 1
    
    print(f"Running {module_name} tests...")
    
    # Load and run tests for specific module
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(module_map[module_name])
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    # Print summary
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / max(result.testsRun, 1)) * 100
    print(f"\n{module_name} Test Summary:")
    print(f"  Tests run: {result.testsRun}")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Success rate: {success_rate:.1f}%")
    
    return 0 if len(result.failures) == 0 and len(result.errors) == 0 else 1


def main():
    """Main entry point for test runner."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Pyferris Comprehensive Test Runner')
    parser.add_argument('--module', '-m', help='Run tests for specific module only')
    parser.add_argument('--verbose', '-v', action='count', default=1,
                       help='Increase verbosity (use -v, -vv for more detail)')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Reduce output verbosity')
    
    args = parser.parse_args()
    
    # Determine verbosity level
    if args.quiet:
        verbosity = 0
    else:
        verbosity = min(args.verbose, 2)
    
    if args.module:
        # Run specific module
        return run_specific_module(args.module, verbosity)
    else:
        # Run all tests
        runner = PyferrisTestRunner()
        return runner.run_all_tests(verbosity)


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
