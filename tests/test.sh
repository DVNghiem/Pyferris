#!/bin/bash
# Pyferris Test Automation Script
# This script provides convenient commands for running tests

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to project root
cd "$PROJECT_ROOT"

# Function to check if Python and dependencies are available
check_dependencies() {
    print_info "Checking dependencies..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed or not in PATH"
        exit 1
    fi
    
    # Check if pyferris is importable
    if ! python3 -c "import pyferris" 2>/dev/null; then
        print_warning "Pyferris module not importable. You may need to build it first."
        print_info "Try running: maturin develop"
    fi
    
    print_success "Dependencies check completed"
}

# Function to run all tests
run_all_tests() {
    print_info "Running all Pyferris tests..."
    cd tests
    python3 test_all.py
    local exit_code=$?
    cd ..
    
    if [ $exit_code -eq 0 ]; then
        print_success "All tests completed successfully!"
    else
        print_error "Some tests failed. Check the output above for details."
    fi
    
    return $exit_code
}

# Function to run quick tests
run_quick_tests() {
    print_info "Running quick tests (core functionality only)..."
    cd tests
    python3 test_all.py --module core --quiet
    local exit_code=$?
    cd ..
    
    if [ $exit_code -eq 0 ]; then
        print_success "Quick tests passed!"
    else
        print_error "Quick tests failed."
    fi
    
    return $exit_code
}

# Function to run specific module tests
run_module_tests() {
    local module=$1
    print_info "Running $module tests..."
    cd tests
    python3 test_all.py --module "$module"
    local exit_code=$?
    cd ..
    
    if [ $exit_code -eq 0 ]; then
        print_success "$module tests passed!"
    else
        print_error "$module tests failed."
    fi
    
    return $exit_code
}

# Function to build and test
build_and_test() {
    print_info "Building Pyferris..."
    
    # Check if maturin is available
    if command -v maturin &> /dev/null; then
        maturin develop
        if [ $? -eq 0 ]; then
            print_success "Build completed successfully"
            run_all_tests
        else
            print_error "Build failed"
            return 1
        fi
    else
        print_warning "maturin not found. Skipping build step."
        print_info "Install maturin with: pip install maturin"
        run_all_tests
    fi
}

# Function to show test coverage summary
show_coverage() {
    print_info "Test coverage summary:"
    echo "  ✅ Core parallel operations (map, filter, reduce, starmap)"
    echo "  ✅ Configuration management (workers, chunk size)"
    echo "  ✅ Simple I/O operations (read, write, copy, move)"
    echo "  ✅ CSV file operations (reader, writer, utilities)"
    echo "  ✅ JSON file operations (reader, writer, JSON Lines)"
    echo "  ✅ Executor functionality (task management)"
    echo "  ✅ Parallel I/O operations (batch processing)"
    echo "  ✅ Error handling and edge cases"
    echo "  ✅ Performance benchmarking"
}

# Function to run performance benchmarks
run_benchmarks() {
    print_info "Running performance benchmarks..."
    cd tests
    python3 test_all.py -v | grep -E "(time|performance|Speedup|seconds)"
    cd ..
    print_success "Benchmark completed"
}

# Function to show help
show_help() {
    echo "Pyferris Test Automation Script"
    echo "==============================="
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  all              Run all tests (default)"
    echo "  quick            Run quick tests (core functionality only)"
    echo "  build            Build project and run all tests"
    echo "  coverage         Show test coverage summary"
    echo "  benchmark        Run performance benchmarks"
    echo "  check            Check dependencies"
    echo ""
    echo "Module-specific tests:"
    echo "  core             Run core parallel operation tests"
    echo "  config           Run configuration management tests"
    echo "  io               Run simple I/O tests"
    echo "  csv              Run CSV operation tests"
    echo "  json             Run JSON operation tests"
    echo "  executor         Run executor functionality tests"
    echo "  parallel         Run parallel I/O tests"
    echo ""
    echo "Examples:"
    echo "  $0               # Run all tests"
    echo "  $0 quick         # Run quick tests"
    echo "  $0 csv           # Run CSV tests only"
    echo "  $0 build         # Build and test"
    echo ""
}

# Main script logic
case "${1:-all}" in
    "all")
        check_dependencies
        run_all_tests
        ;;
    "quick")
        check_dependencies
        run_quick_tests
        ;;
    "build")
        check_dependencies
        build_and_test
        ;;
    "check")
        check_dependencies
        ;;
    "coverage")
        show_coverage
        ;;
    "benchmark")
        check_dependencies
        run_benchmarks
        ;;
    "core"|"config"|"io"|"csv"|"json"|"executor"|"parallel")
        check_dependencies
        # Map 'io' to 'simple_io' and 'parallel' to 'parallel_io'
        case "$1" in
            "io") run_module_tests "simple_io" ;;
            "parallel") run_module_tests "parallel_io" ;;
            *) run_module_tests "$1" ;;
        esac
        ;;
    "help"|"--help"|"-h")
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
