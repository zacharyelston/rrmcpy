#!/usr/bin/env python3
"""
Container-compatible entry point for Redmine MCP Server
Handles asyncio loop conflicts in development environments like Windsurf
"""
import os
import sys
import asyncio
import signal
from typing import Optional

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from mcp_server import RedmineMCPServer
except ImportError as e:
    print(f"Failed to import MCP server: {e}", file=sys.stderr)
    sys.exit(1)


class ContainerMCPServer:
    """Container-safe MCP server wrapper"""
    
    def __init__(self):
        self.server = None
        self.running = False
        
    async def start(self):
        """Start the MCP server in container-safe mode"""
        try:
            self.server = RedmineMCPServer()
            self.server.initialize()
            
            # Set up signal handlers
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            
            print("Redmine MCP Server started in container mode")
            print("Waiting for MCP client connections...")
            
            self.running = True
            
            # Keep the server alive without blocking
            while self.running:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            print("\nServer stopped by user")
        except Exception as e:
            print(f"Server error: {e}", file=sys.stderr)
            raise
        finally:
            self.running = False
            
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\nReceived signal {signum}, shutting down...")
        self.running = False


async def main():
    """Main entry point for container environments"""
    container_server = ContainerMCPServer()
    await container_server.start()


def run_container_server():
    """Entry point that handles existing event loops"""
    try:
        # Check if there's already a running event loop
        loop = asyncio.get_running_loop()
        print("Detected existing event loop - using container compatibility mode")
        
        # Import nest_asyncio for nested loop support
        try:
            import nest_asyncio
            nest_asyncio.apply()
            
            # Create a task in the existing loop
            task = loop.create_task(main())
            return task
        except ImportError:
            print("nest_asyncio not available - installing...")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "nest_asyncio"])
            import nest_asyncio
            nest_asyncio.apply()
            task = loop.create_task(main())
            return task
            
    except RuntimeError:
        # No event loop running, we can start our own
        print("Starting new event loop for MCP server")
        return asyncio.run(main())


if __name__ == "__main__":
    try:
        run_container_server()
    except Exception as e:
        print(f"Failed to start container server: {e}", file=sys.stderr)
        sys.exit(1)