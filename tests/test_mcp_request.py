#!/usr/bin/env python3
"""
Simple script to send a single MCP request to the server
"""
import json
import sys
import subprocess

# Define the request
method = "GET"
path = "/projects"
data = {}

if len(sys.argv) > 1:
    method = sys.argv[1]
if len(sys.argv) > 2:
    path = sys.argv[2]

# Create the request JSON
request = {
    "method": method,
    "path": path,
    "data": data
}

# Print what we're sending
print(f"Sending {method} request to {path}")

# Convert to JSON string
request_json = json.dumps(request)

# Use shell command to pipe the request to main.py
command = f'echo \'{request_json}\' | python main.py'
print(f"Running: {command}")

# Execute the command
result = subprocess.run(command, shell=True, capture_output=True, text=True)

# Print the output
print("\nResponse:")
print(result.stdout)

if result.stderr:
    print("\nErrors:")
    print(result.stderr)