#!/usr/bin/env python3
"""
Test runner for the Redmine MCP Server
This script sets up the environment and runs the tests
"""
import os
import sys
import logging
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_tests(test_args=None):
    """
    Run pytest with the specified arguments
    
    Args:
        test_args: Optional list of arguments to pass to pytest
    """
    if test_args is None:
        test_args = []
    
    # Verify API key is available
    redmine_api_key = os.environ.get('REDMINE_API_KEY', '')
    
    if not redmine_api_key:
        logger.error("REDMINE_API_KEY environment variable is required")
        return 1
    
    # Set default test project
    os.environ['TEST_PROJECT'] = os.environ.get('TEST_PROJECT', 'p1')
    
    # Build the pytest command
    cmd = [
        'python', '-m', 'pytest',
        '-v',
        '--cov=src',
        '--cov-report=term',
        '--cov-report=xml'
    ] + test_args
    
    logger.info(f"Running tests: {' '.join(cmd)}")
    
    # Run pytest
    result = subprocess.run(cmd)
    return result.returncode

def main():
    """Main entry point"""
    # Get command line arguments to pass to pytest
    test_args = sys.argv[1:]
    
    # Run tests
    return run_tests(test_args)

if __name__ == '__main__':
    sys.exit(main())