#!/bin/bash
# Helper script to run tests with proper environment variables

# Check if REDMINE_URL and REDMINE_API_KEY are set
if [ -z "$REDMINE_URL" ] || [ -z "$REDMINE_API_KEY" ]; then
    echo "Warning: REDMINE_URL and/or REDMINE_API_KEY environment variables are not set."
    echo "Live tests will be skipped unless these variables are provided."
    echo ""
fi

# Parse command line arguments
TEST_TYPE="all"
VERBOSE=""

while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        -u|--unit)
            TEST_TYPE="unit"
            shift
            ;;
        -i|--integration)
            TEST_TYPE="integration"
            shift
            ;;
        -l|--live)
            TEST_TYPE="live"
            shift
            ;;
        -v|--verbose)
            VERBOSE="-v"
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  -u, --unit         Run only unit tests"
            echo "  -i, --integration  Run only integration tests"
            echo "  -l, --live         Run only live tests"
            echo "  -v, --verbose      Run tests in verbose mode"
            echo "  -h, --help         Show this help message"
            echo ""
            echo "Environment variables:"
            echo "  REDMINE_URL        URL of the Redmine instance (required for live tests)"
            echo "  REDMINE_API_KEY    API key for the Redmine instance (required for live tests)"
            exit 0
            ;;
        *)
            echo "Unknown option: $key"
            echo "Use --help for usage information."
            exit 1
            ;;
    esac
done

# Run the appropriate tests
case $TEST_TYPE in
    "unit")
        echo "Running unit tests..."
        python -m pytest tests/unit $VERBOSE
        ;;
    "integration")
        echo "Running integration tests..."
        python -m pytest tests/integration $VERBOSE
        ;;
    "live")
        echo "Running live tests..."
        if [ -z "$REDMINE_URL" ] || [ -z "$REDMINE_API_KEY" ]; then
            echo "Error: REDMINE_URL and REDMINE_API_KEY must be set for live tests."
            exit 1
        fi
        python -m pytest tests/live $VERBOSE
        ;;
    "all")
        echo "Running all tests..."
        python -m pytest $VERBOSE
        ;;
esac
