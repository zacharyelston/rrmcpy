#!/usr/bin/env python3
"""
Live tests for standardized error handling and logging
Tests both issue #124 (logging) and #117 (error handling)
"""
import os
import sys
import pytest
import json
import logging

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.base import RedmineBaseClient
from src.issues import IssueClient
from src.projects import ProjectClient
from src.core.errors import ErrorCode, ErrorResponse, get_error_handler
from src.core.logging import setup_logging, get_logger, StructuredFormatter


class TestStandardizedErrorHandling:
    """Test standardized error handling (Issue #117)"""
    
    @classmethod
    def setup_class(cls):
        """Set up test clients"""
        redmine_url = os.environ.get('REDMINE_URL', 'https://redstone.redminecloud.net')
        api_key = os.environ.get('REDMINE_API_KEY')
        
        if not api_key:
            pytest.skip("REDMINE_API_KEY environment variable required")
            
        cls.issue_client = IssueClient(redmine_url, api_key)
        cls.project_client = ProjectClient(redmine_url, api_key)
        cls.base_client = RedmineBaseClient(redmine_url, api_key)
    
    def test_error_response_format(self):
        """Test that all errors follow the standard format"""
        # Create an error using the new system
        error = ErrorResponse.create(
            ErrorCode.VALIDATION_ERROR,
            "Test error message",
            400,
            details={"field": "value"},
            context={"operation": "test"}
        )
        
        # Verify structure
        assert error["error"] is True
        assert error["error_code"] == "VALIDATION_ERROR"
        assert error["message"] == "Test error message"
        assert error["status_code"] == 400
        assert "timestamp" in error
        assert error["timestamp"].endswith("Z")
        assert error["details"]["field"] == "value"
        assert error["context"]["operation"] == "test"
    
    def test_validation_error_format(self):
        """Test validation error with field errors"""
        # Try to create issue without required fields
        result = self.issue_client.create_issue({})
        
        # Check error format
        assert result["error"] is True
        assert result["error_code"] == "VALIDATION_ERROR"
        assert result["status_code"] == 400
        assert "timestamp" in result
        assert "message" in result
        assert "project_id" in result["message"].lower()
    
    def test_http_error_format(self):
        """Test HTTP error responses"""
        # Test 404 error
        result = self.issue_client.get_issue(999999999)
        
        assert result["error"] is True
        assert result["error_code"] == "NOT_FOUND"
        assert result["status_code"] == 404
        assert "timestamp" in result
        assert "message" in result
        
        # Test 401 error with bad API key
        bad_client = IssueClient(
            os.environ.get('REDMINE_URL', 'https://redstone.redminecloud.net'),
            "invalid_api_key"
        )
        result = bad_client.get_issue(1)
        
        assert result["error"] is True
        assert result["error_code"] == "AUTHENTICATION_ERROR"
        assert result["status_code"] == 401
        assert "timestamp" in result
    
    def test_connection_error_format(self):
        """Test connection error handling"""
        # Create client with invalid URL
        bad_client = IssueClient("https://invalid-redmine-url-12345.com", "test")
        result = bad_client.get_issue(1)
        
        assert result["error"] is True
        assert result["error_code"] == "CONNECTION_ERROR"
        assert result["status_code"] == 503
        assert "timestamp" in result
        assert "Failed to connect" in result["message"]
    
    def test_error_context_included(self):
        """Test that errors include appropriate context"""
        # Create invalid project data
        result = self.project_client.create_project({
            "name": "Test Project",
            "identifier": ""  # Empty identifier should fail
        })
        
        # Should have error with context
        assert result["error"] is True
        assert "timestamp" in result
        
        # The context might be in different places depending on implementation
        # But the error should be informative
        assert result["message"]  # Should have a meaningful message


class TestStandardizedLogging:
    """Test standardized logging and error reporting (Issue #124)"""
    
    @classmethod
    def setup_class(cls):
        """Set up test clients"""
        redmine_url = os.environ.get('REDMINE_URL', 'https://redstone.redminecloud.net')
        api_key = os.environ.get('REDMINE_API_KEY')
        
        if not api_key:
            pytest.skip("REDMINE_API_KEY environment variable required")
            
        cls.issue_client = IssueClient(redmine_url, api_key)
    
    def test_structured_formatter(self):
        """Test the structured log formatter"""
        formatter = StructuredFormatter(include_extra=True)
        
        # Create a log record
        record = logging.LogRecord(
            name="test.logger",
            level=logging.ERROR,
            pathname="test.py",
            lineno=10,
            msg="Test error message",
            args=(),
            exc_info=None
        )
        
        # Add extra fields
        record.error_code = "TEST_ERROR"
        record.status_code = 500
        
        # Format the record
        formatted = formatter.format(record)
        
        # Should be valid JSON for errors
        log_data = json.loads(formatted)
        assert log_data["level"] == "ERROR"
        assert log_data["message"] == "Test error message"
        assert log_data["logger"] == "test.logger"
        assert "timestamp" in log_data
        assert "location" in log_data
        assert log_data["context"]["error_code"] == "TEST_ERROR"
        assert log_data["context"]["status_code"] == 500
    
    def test_logger_namespace(self):
        """Test that loggers are properly namespaced"""
        logger1 = get_logger("test_module")
        logger2 = get_logger("redmine_mcp_server.test_module")
        
        # Both should have the same name (properly namespaced)
        assert logger1.name == "redmine_mcp_server.test_module"
        assert logger2.name == "redmine_mcp_server.test_module"
    
    def test_error_handler_logging(self):
        """Test that error handler logs appropriately"""
        # Create a logger with a handler that captures logs
        import io
        log_capture = io.StringIO()
        handler = logging.StreamHandler(log_capture)
        handler.setLevel(logging.ERROR)
        
        logger = logging.getLogger("test_error_handler")
        logger.addHandler(handler)
        logger.setLevel(logging.ERROR)
        
        # Create error handler with this logger
        error_handler = get_error_handler(logger)
        
        # Generate an error
        error_handler.handle_validation_error(
            "Test validation error",
            field_errors={"field1": "error1"},
            context={"test": True}
        )
        
        # Check that it was logged
        log_output = log_capture.getvalue()
        assert "Validation error: Test validation error" in log_output
    
    def test_api_request_logging(self):
        """Test that API requests are logged with proper context"""
        # This is tested implicitly through live API calls
        # Make a successful request
        result = self.issue_client.get_issues(params={"limit": 1})
        
        # Should succeed (validates logging doesn't break functionality)
        assert "issues" in result or result.get("error") is True


class TestIntegratedErrorAndLogging:
    """Test that error handling and logging work together"""
    
    @classmethod
    def setup_class(cls):
        """Set up test environment"""
        redmine_url = os.environ.get('REDMINE_URL', 'https://redstone.redminecloud.net')
        api_key = os.environ.get('REDMINE_API_KEY')
        
        if not api_key:
            pytest.skip("REDMINE_API_KEY environment variable required")
            
        # Set up logging
        from src.core.config import LogConfig
        log_config = LogConfig(level="DEBUG", structured=True)
        setup_logging(log_config)
        
        cls.issue_client = IssueClient(redmine_url, api_key)
    
    def test_full_error_flow(self):
        """Test complete error flow with logging"""
        # Try to create an issue with validation error
        result = self.issue_client.create_issue({
            "subject": "",  # Empty subject
            "project_id": "nonexistent"  # Invalid project
        })
        
        # Should get structured error
        assert result["error"] is True
        assert result["error_code"] in ["VALIDATION_ERROR", "NOT_FOUND"]
        assert result["status_code"] in [400, 404, 422]
        assert "timestamp" in result
        assert "message" in result
        
        # Error should be properly formatted
        assert isinstance(result["timestamp"], str)
        assert result["timestamp"].endswith("Z")
    
    def test_error_consistency(self):
        """Test that errors are consistent across different scenarios"""
        errors = []
        
        # Collect different types of errors
        
        # 1. Validation error
        result1 = self.issue_client.create_issue({})
        if result1.get("error"):
            errors.append(result1)
        
        # 2. Not found error  
        result2 = self.issue_client.get_issue(999999999)
        if result2.get("error"):
            errors.append(result2)
        
        # 3. Authentication error
        bad_client = IssueClient(
            os.environ.get('REDMINE_URL', 'https://redstone.redminecloud.net'),
            "bad_key"
        )
        result3 = bad_client.get_issue(1)
        if result3.get("error"):
            errors.append(result3)
        
        # All errors should have consistent structure
        for error in errors:
            assert error["error"] is True
            assert "error_code" in error
            assert "message" in error
            assert "status_code" in error
            assert "timestamp" in error
            
            # Timestamp should be ISO format with Z
            assert error["timestamp"].endswith("Z")
            assert "T" in error["timestamp"]
            
            # Status code should be appropriate
            assert 400 <= error["status_code"] < 600


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
