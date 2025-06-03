#!/usr/bin/env python3
"""
Test script for the new modular Redmine MCP Server architecture
"""
import sys
import os
import asyncio
import logging

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.config import AppConfig, RedmineConfig, LogConfig, ServerConfig
from core.logging import setup_logging
from services.issue_service import IssueService
from issues import IssueClient
from tools.registry import ToolRegistry
from tools.issue_tools import CreateIssueTool, GetIssueTool, ListIssuesTool
from tools.admin_tools import HealthCheckTool


def test_configuration():
    """Test configuration loading"""
    print("Testing configuration system...")
    
    try:
        # Test individual configs
        redmine_config = RedmineConfig(
            url="https://test.example.com",
            api_key="test_key_123"
        )
        
        log_config = LogConfig(level="DEBUG")
        server_config = ServerConfig(mode="test")
        
        # Test complete app config
        app_config = AppConfig(
            redmine=redmine_config,
            logging=log_config,
            server=server_config
        )
        
        print("✓ Configuration system working")
        return app_config
        
    except Exception as e:
        print(f"✗ Configuration failed: {e}")
        return None


def test_logging():
    """Test logging setup"""
    print("Testing logging system...")
    
    try:
        log_config = LogConfig(level="DEBUG")
        logger = setup_logging(log_config)
        
        logger.debug("Debug message test")
        logger.info("Info message test")
        logger.warning("Warning message test")
        
        print("✓ Logging system working")
        return logger
        
    except Exception as e:
        print(f"✗ Logging failed: {e}")
        return None


def test_tool_registry():
    """Test tool registry system"""
    print("Testing tool registry...")
    
    try:
        # Create mock service for testing
        class MockService:
            def __init__(self):
                self.config = RedmineConfig(url="https://test.com", api_key="test")
            
            def create_issue(self, data):
                return {"success": True, "data": {"id": 123, "subject": data.get("subject")}}
            
            def get_issue(self, issue_id, include=None):
                return {"success": True, "data": {"id": issue_id, "subject": "Test Issue"}}
            
            def list_issues(self, filters=None):
                return {"success": True, "data": [{"id": 1, "subject": "Issue 1"}]}
        
        # Create tool registry
        registry = ToolRegistry()
        mock_service = MockService()
        
        # Register tools
        registry.register(CreateIssueTool, mock_service)
        registry.register(GetIssueTool, mock_service)
        registry.register(ListIssuesTool, mock_service)
        registry.register(HealthCheckTool, mock_service)
        
        # Test tool registration
        tools = registry.get_all_tools()
        tool_names = registry.list_tool_names()
        
        print(f"✓ Registered {len(tools)} tools: {', '.join(tool_names)}")
        
        # Test tool execution
        result = registry.execute_tool("redmine-create-issue", 
                                     project_id="test", 
                                     subject="Test Issue")
        print(f"✓ Tool execution test: {result}")
        
        return registry
        
    except Exception as e:
        print(f"✗ Tool registry failed: {e}")
        return None


def test_service_layer():
    """Test service layer"""
    print("Testing service layer...")
    
    try:
        # Create mock issue client
        class MockIssueClient:
            def __init__(self, base_url, api_key, logger=None):
                self.base_url = base_url
                self.api_key = api_key
                self.logger = logger
            
            def create_issue(self, data):
                return {"issue": {"id": 123, "subject": data.get("subject")}}
            
            def get_issue(self, issue_id, include=None):
                return {"issue": {"id": issue_id, "subject": "Mock Issue"}}
            
            def get_issues(self, params=None):
                return {"issues": [{"id": 1, "subject": "Mock Issue 1"}]}
            
            def health_check(self):
                return True
        
        # Test service creation
        config = RedmineConfig(url="https://test.com", api_key="test")
        mock_client = MockIssueClient("https://test.com", "test")
        
        service = IssueService(config, mock_client)
        
        # Test service methods
        create_result = service.create_issue({
            "project_id": "test",
            "subject": "Test Service Issue"
        })
        
        get_result = service.get_issue(123)
        
        list_result = service.list_issues({"limit": 10})
        
        print("✓ Service layer working")
        print(f"  Create result: {create_result.get('success', False)}")
        print(f"  Get result: {get_result.get('success', False)}")
        print(f"  List result: {list_result.get('success', False)}")
        
        return service
        
    except Exception as e:
        print(f"✗ Service layer failed: {e}")
        return None


async def test_server_initialization():
    """Test server initialization without actually running it"""
    print("Testing server initialization...")
    
    try:
        # Set test environment variables
        os.environ['REDMINE_URL'] = 'https://test.example.com'
        os.environ['REDMINE_API_KEY'] = 'test_key_123'
        os.environ['SERVER_MODE'] = 'test'
        os.environ['LOG_LEVEL'] = 'DEBUG'
        
        # Import and test server (without running)
        from mcp_server import RedmineMCPServer
        
        server = RedmineMCPServer()
        
        # Test configuration loading
        server.config = AppConfig.from_environment()
        print(f"✓ Server config loaded: {server.config.server.mode} mode")
        
        # Test logging setup
        server.logger = setup_logging(server.config.logging)
        print("✓ Server logging initialized")
        
        # Test tool registry
        server.tool_registry = ToolRegistry(server.logger)
        print("✓ Tool registry created")
        
        print("✓ Server initialization test completed")
        return True
        
    except Exception as e:
        print(f"✗ Server initialization failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 50)
    print("Testing Modular Redmine MCP Server Architecture")
    print("=" * 50)
    
    # Run tests
    tests = [
        test_configuration,
        test_logging,
        test_service_layer,
        test_tool_registry,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result is not None)
            print()
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
            results.append(False)
            print()
    
    # Run async test
    try:
        async_result = asyncio.run(test_server_initialization())
        results.append(async_result)
        print()
    except Exception as e:
        print(f"✗ Async test crashed: {e}")
        results.append(False)
        print()
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! Modular architecture is working correctly.")
    else:
        print(f"✗ {total - passed} tests failed. Check the errors above.")
    
    print("=" * 50)
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)