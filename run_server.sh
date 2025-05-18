#!/bin/bash
# Entry point shell script for Redmine MCP Server
# This script passes all arguments to the Python module in src
python3 -m src.main "$@"