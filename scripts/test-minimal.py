#!/usr/bin/env python3
"""
Minimal health check script for Redmine MCP Server
Tests basic server initialization and tool registration
"""
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_server_initialization():
    """Test basic server initialization"""
    try:
        from src.mcp_server import RedmineMCPServer
        print("✓ Server imports successfully")
        
        # Test initialization
        server = RedmineMCPServer()
        print("✓ Server initializes without errors")
        
        # Check if tools are properly registered
        if hasattr(server, 'tool_registry') and server.tool_registry:
            tool_count = len(server.tool_registry.tools)
            print(f"✓ Tool registry initialized with {tool_count} tools")
        else:
            print("⚠ Tool registry not properly initialized")
            
        return True
        
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Server initialization failed: {e}")
        return False

def test_module_imports():
    """Test that all core modules import correctly"""
    modules_to_test = [
        'src.core.config',
        'src.core.errors', 
        'src.services.base_service',
        'src.services.issue_service',
        'src.tools.base_tool',
        'src.tools.registry',
        'src.tools.issue_tools',
        'src.tools.admin_tools'
    ]
    
    success_count = 0
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"✓ {module}")
            success_count += 1
        except ImportError as e:
            print(f"✗ {module}: {e}")
    
    print(f"\nModule import results: {success_count}/{len(modules_to_test)} successful")
    return success_count == len(modules_to_test)

def main():
    """Run minimal health checks"""
    print("=== Redmine MCP Server - Minimal Health Check ===\n")
    
    print("1. Testing module imports...")
    modules_ok = test_module_imports()
    
    print("\n2. Testing server initialization...")
    server_ok = test_server_initialization()
    
    print("\n=== Results ===")
    if modules_ok and server_ok:
        print("✓ All basic health checks passed")
        print("✓ Server is ready for operation")
        return 0
    else:
        print("✗ Some health checks failed")
        print("✗ Server may not function properly")
        return 1

if __name__ == "__main__":
    sys.exit(main())