"""
Entry point for Redmine MCPServer FlaskUI

This provides a web UI for interacting with the Redmine MCPServer.
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import json
import logging
import sys

# Add src directory to path to allow importing from redmine_mcpserver
sys.path.append('.')

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "redmine-mcp-server-dev-key")

@app.route('/')
def index():
    """Render the main dashboard page"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "version": "1.0.0"})

@app.route('/api/redmine/status')
def redmine_status():
    """Check Redmine connection status"""
    from src.redmine_mcpserver.redmine_api import RedmineAPI
    
    try:
        redmine_url = os.environ.get("REDMINE_URL", "https://redstone.redminecloud.net")
        redmine_api_key = os.environ.get("REDMINE_API_KEY", "")
        
        if not redmine_api_key:
            return jsonify({"status": "error", "message": "Redmine API key not configured"})
        
        # Initialize client and check connection
        client = RedmineAPI(redmine_url, redmine_api_key)
        current_user = client.get_current_user()
        
        return jsonify({
            "status": "ok", 
            "message": f"Connected to Redmine as {current_user.get('user', {}).get('login', 'unknown')}"
        })
    except Exception as e:
        logger.error(f"Error checking Redmine status: {e}")
        return jsonify({"status": "error", "message": str(e)})

# Create templates directory if it doesn't exist
if not os.path.exists('templates'):
    os.makedirs('templates')

# Create index.html if it doesn't exist
index_html_path = os.path.join('templates', 'index.html')
if not os.path.exists(index_html_path):
    with open(index_html_path, 'w') as f:
        f.write("""<!DOCTYPE html>
<html data-bs-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Redmine MCP Server Dashboard</title>
    <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-4">
        <div class="row mb-4">
            <div class="col">
                <h1>Redmine MCP Server Dashboard</h1>
                <p class="text-muted">Monitor and control your Redmine MCPServer</p>
                <div id="status-badge" class="badge bg-secondary">Checking status...</div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-md-6">
                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="card-title">Redmine Connection</h5>
                    </div>
                    <div class="card-body">
                        <div id="redmine-status">Checking connection...</div>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6">
                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="card-title">MCPServer Status</h5>
                    </div>
                    <div class="card-body">
                        <p>Server mode: <span class="badge bg-info">Web UI</span></p>
                        <p>MCP protocol: <strong>STDIO</strong></p>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col">
                <div class="card">
                    <div class="card-header">
                        <h5 class="card-title">Documentation</h5>
                    </div>
                    <div class="card-body">
                        <p>The Redmine MCP Server provides a server implementation of the MCP protocol for Redmine.</p>
                        
                        <h6>Features:</h6>
                        <ul>
                            <li>Communicate with Redmine over FastMCP protocol</li>
                            <li>Manage issues, projects, versions, users and groups</li>
                            <li>Support for roadmap and version planning</li>
                            <li>Docker containerization for easy deployment</li>
                        </ul>
                        
                        <h6>Environment Variables:</h6>
                        <ul>
                            <li><code>REDMINE_URL</code> - URL of the Redmine instance</li>
                            <li><code>REDMINE_API_KEY</code> - API key for Redmine authentication</li>
                            <li><code>SERVER_MODE</code> - Server mode (live or test)</li>
                            <li><code>LOG_LEVEL</code> - Logging level (debug, info, warning, error)</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Check Redmine connection status
        fetch('/api/redmine/status')
            .then(response => response.json())
            .then(data => {
                const statusElement = document.getElementById('redmine-status');
                const statusBadge = document.getElementById('status-badge');
                
                if (data.status === 'ok') {
                    statusElement.innerHTML = `<div class="alert alert-success">${data.message}</div>`;
                    statusBadge.className = 'badge bg-success';
                    statusBadge.textContent = 'Connected';
                } else {
                    statusElement.innerHTML = `<div class="alert alert-danger">${data.message}</div>`;
                    statusBadge.className = 'badge bg-danger';
                    statusBadge.textContent = 'Disconnected';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                document.getElementById('redmine-status').innerHTML = 
                    `<div class="alert alert-danger">Error checking Redmine status: ${error.message}</div>`;
                
                const statusBadge = document.getElementById('status-badge');
                statusBadge.className = 'badge bg-danger';
                statusBadge.textContent = 'Error';
            });
    </script>
</body>
</html>""")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)