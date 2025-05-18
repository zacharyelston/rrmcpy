"""
MCP Client for interacting with the Redmine MCP Server
"""
import json
import logging
import subprocess
import time
from typing import Dict, List, Optional, Any, Union

class MCPClient:
    """
    Client for interacting with a Redmine MCP Server process
    Uses standard input/output for communication
    """
    def __init__(self, server_command: List[str], logger: Optional[logging.Logger] = None):
        """
        Initialize the MCP client
        
        Args:
            server_command: Command to start the MCP server (e.g., ["python", "main.py"])
            logger: Optional logger instance
        """
        self.server_command = server_command
        self.logger = logger or logging.getLogger(__name__)
        self.server_process = None
        
    def start_server(self):
        """Start the MCP server process"""
        if self.server_process and self.server_process.poll() is None:
            self.logger.warning("Server process is already running")
            return
            
        self.logger.info(f"Starting MCP server with command: {' '.join(self.server_command)}")
        self.server_process = subprocess.Popen(
            self.server_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            bufsize=1  # Line buffered
        )
        
    def stop_server(self):
        """Stop the MCP server process"""
        if self.server_process and self.server_process.poll() is None:
            self.logger.info("Stopping MCP server")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.logger.warning("Server did not terminate gracefully, killing it")
                self.server_process.kill()
        
    def send_request(self, method: str, path: str, data: Optional[Dict] = None) -> Dict:
        """
        Send a request to the MCP server
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            path: Path to request
            data: Optional data to send
            
        Returns:
            Response from the server
        """
        if not self.server_process or self.server_process.poll() is not None:
            self.start_server()
            # Give the server a moment to initialize
            time.sleep(1)
            
        # Make sure server process is running
        if not self.server_process:
            self.logger.error("Failed to start server process")
            return {"status": 500, "data": {"error": "Failed to start server process"}}
            
        # Build the request
        request = {
            'method': method,
            'path': path
        }
        if data:
            request['data'] = data
            
        # Convert to JSON and send
        request_json = json.dumps(request)
        self.logger.debug(f"Sending request: {request_json}")
        
        try:
            # Check if the server is ready to accept input
            if not self.server_process.stdin:
                self.logger.error("Server process stdin is not available")
                return {"status": 500, "data": {"error": "Server process stdin is not available"}}
                
            if not self.server_process.stdout:
                self.logger.error("Server process stdout is not available")
                return {"status": 500, "data": {"error": "Server process stdout is not available"}}
                
            # Write the request to stdin
            self.server_process.stdin.write(request_json + '\n')
            self.server_process.stdin.flush()
            
            # Read the response from stdout
            response_line = self.server_process.stdout.readline().strip()
            self.logger.debug(f"Received response: {response_line}")
            
            # Parse the response
            if not response_line:
                self.logger.error("Empty response from server")
                return {"status": 500, "data": {"error": "Empty response from server"}}
                
            response = json.loads(response_line)
            
            # Check for error status
            if response.get('status', 500) >= 400:
                error_msg = response.get('data', {}).get('error', 'Unknown error')
                self.logger.error(f"MCP server error: {error_msg}")
                
            return response
        except Exception as e:
            self.logger.error(f"Error communicating with MCP server: {e}")
            return {"status": 500, "data": {"error": str(e)}}
            
    # Helper methods for common operations
    
    def health_check(self) -> Dict:
        """Check the health of the MCP server"""
        return self.send_request('GET', '/health')
        
    def get_issues(self, params: Optional[Dict] = None) -> Dict:
        """Get a list of issues with optional filtering"""
        return self.send_request('GET', '/issues', params)
        
    def get_issue(self, issue_id: int) -> Dict:
        """Get a specific issue by ID"""
        return self.send_request('GET', f'/issues/{issue_id}')
        
    def create_issue(self, issue_data: Dict) -> Dict:
        """Create a new issue"""
        return self.send_request('POST', '/issues', issue_data)
        
    def update_issue(self, issue_id: int, issue_data: Dict) -> Dict:
        """Update an existing issue"""
        return self.send_request('PUT', f'/issues/{issue_id}', issue_data)
        
    def delete_issue(self, issue_id: int) -> Dict:
        """Delete an issue"""
        return self.send_request('DELETE', f'/issues/{issue_id}')
        
    def get_projects(self) -> Dict:
        """Get a list of projects"""
        return self.send_request('GET', '/projects')
        
    def get_project(self, project_id: Union[int, str]) -> Dict:
        """Get a specific project by ID or identifier"""
        return self.send_request('GET', f'/projects/{project_id}')
        
    def get_versions(self, project_id: Union[int, str]) -> Dict:
        """Get versions for a project"""
        return self.send_request('GET', f'/projects/{project_id}/versions')
        
    def create_version(self, project_id: Union[int, str], version_data: Dict) -> Dict:
        """Create a new version for a project"""
        return self.send_request('POST', f'/projects/{project_id}/versions', version_data)
        
    def tag_issue_with_version(self, issue_id: int, version_id: int) -> Dict:
        """Tag an issue with a version (fixed_version_id)"""
        return self.send_request('PUT', f'/issues/{issue_id}', {"fixed_version_id": version_id})
        
    def get_current_user(self) -> Dict:
        """Get the current user (based on API key)"""
        return self.send_request('GET', '/users/current')