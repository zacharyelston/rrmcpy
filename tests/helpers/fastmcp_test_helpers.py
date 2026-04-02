"""
FastMCP test helpers for setting up proper test context

These helpers make it easier to run tests that require a FastMCP context
without encountering the "No active context found" error.
"""
import asyncio
from functools import wraps
import fastmcp
from fastmcp.server import dependencies
from fastmcp.server.context import Context, _current_context
from typing import Any, Callable, TypeVar, cast

# Type variables for better type hints
T = TypeVar('T')
AsyncFunc = TypeVar('AsyncFunc', bound=Callable[..., Any])

def with_fastmcp_context(func: AsyncFunc) -> Callable[..., Any]:
    """
    Decorator to run an async function with a FastMCP context.
    
    This solves the "No active context found" error when calling FastMCP
    methods directly in tests with asyncio.run().
    
    Args:
        func: The async function to wrap
    
    Returns:
        A wrapped function that sets up the proper FastMCP context
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        async def run_with_context():
            # Create a new context for this test
            # Context only accepts a 'fastmcp' parameter
            ctx = Context(fastmcp=True)
            
            # Set the context as the current context
            token = _current_context.set(ctx)
            try:
                # Run the actual test function with the context
                return await func(*args, **kwargs)
            finally:
                # Always clean up the context
                _current_context.reset(token)
        
        # Run the wrapped function with asyncio
        return asyncio.run(run_with_context())
    
    return wrapper


def run_async_with_context(async_func, *args, **kwargs):
    """
    Run an async function with a FastMCP context.
    
    This is an alternative to the decorator if you don't want to decorate your functions.
    
    Args:
        async_func: The async function to run
        *args: Arguments to pass to the async function
        **kwargs: Keyword arguments to pass to the async function
    
    Returns:
        The result of the async function
    """
    @with_fastmcp_context
    async def wrapped():
        return await async_func(*args, **kwargs)
    
    return wrapped()
