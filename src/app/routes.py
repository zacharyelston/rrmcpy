"""
Redmine MCP Server Web UI routes
Provides API endpoints for the web interface
"""
from flask import render_template, request, jsonify
import os
import logging
import json
import subprocess
from src.app import app

# Configure logging
logger = logging.getLogger(__name__)

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
    try:
        from src.redmine_api import RedmineAPI
        
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

@app.route('/api/server/status')
def server_status():
    """Get MCP server status"""
    try:
        # Check if the MCP server is running by looking for the process
        result = subprocess.run(
            ["pgrep", "-f", "python.*redmine_mcp_server.py"], 
            capture_output=True, 
            text=True
        )
        
        is_running = result.returncode == 0
        
        return jsonify({
            "status": "ok",
            "running": is_running,
            "pid": result.stdout.strip() if is_running else None
        })
    except Exception as e:
        logger.error(f"Error checking server status: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/server/start', methods=['POST'])
def start_server():
    """Start the MCP server"""
    try:
        # Check if already running
        result = subprocess.run(
            ["pgrep", "-f", "python.*redmine_mcp_server.py"], 
            capture_output=True, 
            text=True
        )
        
        if result.returncode == 0:
            return jsonify({
                "status": "ok",
                "message": "Server is already running",
                "pid": result.stdout.strip()
            })
        
        # Start the server as a background process
        process = subprocess.Popen(
            ["python", "redmine_mcp_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=os.environ.copy()
        )
        
        return jsonify({
            "status": "ok",
            "message": "Server started",
            "pid": process.pid
        })
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/server/stop', methods=['POST'])
def stop_server():
    """Stop the MCP server"""
    try:
        # Check if running
        result = subprocess.run(
            ["pgrep", "-f", "python.*redmine_mcp_server.py"], 
            capture_output=True, 
            text=True
        )
        
        if result.returncode != 0:
            return jsonify({
                "status": "ok",
                "message": "Server is not running"
            })
        
        # Kill the server process
        pid = result.stdout.strip()
        subprocess.run(["kill", pid])
        
        return jsonify({
            "status": "ok",
            "message": f"Server stopped (PID: {pid})"
        })
    except Exception as e:
        logger.error(f"Error stopping server: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/config', methods=['GET', 'POST'])
def config():
    """Get or update MCP server configuration"""
    config_file = 'mcp_config.json'
    
    if request.method == 'GET':
        # Get current config
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
            else:
                config_data = {
                    "redmine_url": os.environ.get("REDMINE_URL", "https://redstone.redminecloud.net"),
                    "server_mode": os.environ.get("SERVER_MODE", "live"),
                    "log_level": os.environ.get("LOG_LEVEL", "debug")
                }
            return jsonify({"status": "ok", "config": config_data})
        except Exception as e:
            logger.error(f"Error getting configuration: {e}")
            return jsonify({"status": "error", "message": str(e)})
    else:
        # Update config
        try:
            data = request.get_json()
            
            # Validate required fields
            if not data or not isinstance(data, dict):
                return jsonify({"status": "error", "message": "Invalid configuration data"})
                
            # Save config
            with open(config_file, 'w') as f:
                json.dump(data, f, indent=2)
                
            return jsonify({"status": "ok", "message": "Configuration updated"})
        except Exception as e:
            logger.error(f"Error updating configuration: {e}")
            return jsonify({"status": "error", "message": str(e)})