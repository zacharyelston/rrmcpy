# rrmcpy - Improved Architecture Design

## Overview

This document outlines an improved architecture for the rrmcpy project that follows software design principles focused on simplicity, maintainability, and clarity over complexity ("Built for Clarity"). It leverages FastMCP's native capabilities while providing a clean interface to Redmica.

## Core Design Goals

1. **Simplicity** - Create a design that minimizes complexity while maintaining functionality
2. **Maintainability** - Ensure the codebase is easy to understand, debug, and extend
3. **FastMCP Alignment** - Fully leverage FastMCP's design patterns and capabilities
4. **Redmica Integration** - Provide a comprehensive and reliable interface to Redmica
5. **Developer Experience** - Create an API that's intuitive and easy to use

## Measurable Success Criteria

1. **Code Complexity Metrics**:
   - Cyclomatic complexity < 10 per function
   - Maximum nesting depth < 3 levels
   - Function length < 50 lines

2. **Architecture Metrics**:
   - Maximum of 3 layers between API and implementation
   - No redundant implementations of the same functionality
   - 100% of tools use FastMCP native patterns

3. **Quality Metrics**:
   - Test coverage > 80%
   - Zero lint warnings
   - Documentation for all public interfaces

4. **User Experience Metrics**:
   - Zero redundant parameters in tool definitions
   - Consistent error reporting pattern
   - All tools discoverable through FastMCP's introspection

## Simplified Layer Architecture

```
┌─────────────────────────────────────┐
│        FastMCP Tool Interface       │
└───────────────────┬─────────────────┘
                    │
┌───────────────────▼─────────────────┐
│       Domain Services Layer         │
└───────────────────┬─────────────────┘
                    │
┌───────────────────▼─────────────────┐
│         Redmica API Client          │
└─────────────────────────────────────┘
```

## Core Component Design

### 1. Configuration Management

```python
@dataclass
class RedmineConfig:
    url: str
    api_key: str
    timeout: int = 30
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        if not self.url:
            raise ValueError("Redmine URL is required")
        if not self.api_key:
            raise ValueError("Redmine API key is required")
        
        # Clean URL
        self.url = self.url.rstrip('/')
```

### 2. FastMCP Integration Module

```python
class RedmineServer:
    def __init__(self, config):
        self.config = config
        self.server = FastMCP("Redmine MCP Server")
        
        # Set up lifespan management
        self.server.lifespan = self._lifespan
        
        # Initialize API client
        self.client = RedmineClient(
            url=config.redmine.url,
            api_key=config.redmine.api_key
        )
        
        # Initialize services with client
        self.issue_service = IssueService(self.client)
        self.project_service = ProjectService(self.client)
        
        # Register tools
        self._register_tools()
    
    @asynccontextmanager
    async def _lifespan(self, server):
        # Setup resources
        await self.client.initialize()
        yield
        # Cleanup resources
        await self.client.close()
    
    def _register_tools(self):
        # Register tools using native FastMCP decorators
        self._register_issue_tools()
        self._register_project_tools()
        
    async def run(self, transport="stdio"):
        """Run the MCP server"""
        try:
            # Perform health check
            is_healthy = await self.client.health_check()
            if not is_healthy:
                raise ConnectionError("Redmine API is not accessible")
                
            # Run with specified transport
            await self.server.run(transport)
            
        except Exception as e:
            self.server.logger.error(f"Server error: {e}")
            raise
```

### 3. Domain Service Layer

```python
class IssueService:
    def __init__(self, client):
        self.client = client
    
    async def create_issue(self, project_id, subject, **kwargs):
        """Business logic for issue creation"""
        # Validate input
        if not project_id or not subject:
            raise ValueError("Project ID and subject are required")
            
        # Prepare data
        issue_data = {"project_id": project_id, "subject": subject, **kwargs}
        
        # Execute and return result
        return await self.client.create_issue(issue_data)
        
    async def get_issue(self, issue_id, include=None):
        """Get issue by ID with optional includes"""
        return await self.client.get_issue(issue_id, include)
        
    async def list_issues(self, **filters):
        """List issues with filtering"""
        return await self.client.get_issues(filters)
        
    async def update_issue(self, issue_id, **fields):
        """Update an existing issue"""
        return await self.client.update_issue(issue_id, fields)
        
    async def delete_issue(self, issue_id):
        """Delete an issue"""
        return await self.client.delete_issue(issue_id)
```

### 4. API Client Layer

```python
class RedmineClient:
    def __init__(self, url, api_key, timeout=30):
        self.url = url
        self.api_key = api_key
        self.timeout = timeout
        self.session = None
        
    async def initialize(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession(
            headers={"X-Redmine-API-Key": self.api_key}
        )
        
    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            
    async def health_check(self):
        """Check if Redmine API is accessible"""
        try:
            response = await self.session.get(
                f"{self.url}/users/current.json",
                timeout=self.timeout
            )
            return response.status == 200
        except Exception:
            return False
            
    async def create_issue(self, issue_data):
        """Create a new issue"""
        response = await self.session.post(
            f"{self.url}/issues.json",
            json={"issue": issue_data},
            timeout=self.timeout
        )
        
        if response.status != 201:
            error_data = await response.json()
            raise ApiError(f"Failed to create issue: {error_data}")
            
        return await response.json()
        
    # Additional API methods for other operations...
```

### 5. FastMCP Tool Registration

```python
def _register_issue_tools(self):
    @self.server.tool("redmine-create-issue")
    async def create_issue(
        project_id: str, 
        subject: str, 
        description: str = None,
        tracker_id: int = None,
        status_id: int = None,
        priority_id: int = None,
        assigned_to_id: int = None
    ):
        """Create a new issue in Redmine"""
        try:
            result = await self.issue_service.create_issue(
                project_id=project_id,
                subject=subject,
                description=description,
                tracker_id=tracker_id,
                status_id=status_id,
                priority_id=priority_id,
                assigned_to_id=assigned_to_id
            )
            return result
        except Exception as e:
            self.server.logger.error(f"Error creating issue: {e}")
            return {"error": str(e), "success": False}
            
    @self.server.tool("redmine-get-issue")
    async def get_issue(issue_id: int, include: list = None):
        """Get a specific issue by ID"""
        try:
            result = await self.issue_service.get_issue(issue_id, include)
            return result
        except Exception as e:
            self.server.logger.error(f"Error getting issue {issue_id}: {e}")
            return {"error": str(e), "success": False}
```

### 6. FastMCP Resource Implementation

```python
def _register_resources(self):
    @self.server.resource_template("redmine-issue")
    async def issue_template():
        """Define the schema for a Redmine issue"""
        return {
            "schema": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "project": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "name": {"type": "string"}
                        }
                    },
                    "subject": {"type": "string"},
                    "description": {"type": "string"},
                    "status": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "name": {"type": "string"}
                        }
                    },
                    # Additional properties...
                }
            }
        }
        
    @self.server.resource("redmine-issue", "{issue_id}")
    async def get_issue_resource(issue_id: str):
        """Resource to get a specific issue"""
        try:
            result = await self.issue_service.get_issue(int(issue_id))
            # Transform to match template schema
            return {
                "id": result["issue"]["id"],
                "project": result["issue"]["project"],
                "subject": result["issue"]["subject"],
                "description": result["issue"].get("description", ""),
                "status": result["issue"].get("status", {}),
                # Additional fields...
            }
        except Exception as e:
            self.server.logger.error(f"Error getting issue resource {issue_id}: {e}")
            raise
```

## Error Handling Strategy

```python
class ApiError(Exception):
    """API-related errors with context"""
    def __init__(self, message, status_code=None, details=None):
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)
        
def handle_api_error(func):
    """Decorator for consistent API error handling"""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except aiohttp.ClientError as e:
            raise ApiError(f"Network error: {e}", details={"original_error": str(e)})
        except json.JSONDecodeError:
            raise ApiError("Invalid JSON response from API")
        except Exception as e:
            # Rethrow ApiErrors as is
            if isinstance(e, ApiError):
                raise
            raise ApiError(f"Unexpected error: {e}", details={"original_error": str(e)})
    return wrapper
```

## Implementation Strategy

1. **Phase 1: Architectural Refactoring**
   - Remove the custom ToolRegistry
   - Simplify the layering structure
   - Implement proper FastMCP lifespan management

2. **Phase 2: Service Layer Enhancement**
   - Refine services to include proper validation
   - Add comprehensive error handling
   - Implement consistent logging

3. **Phase 3: Tool Implementation**
   - Convert all tools to use native FastMCP patterns
   - Implement FastMCP's resource system
   - Add proper schema validation

4. **Phase 4: Quality Assurance**
   - Implement comprehensive testing
   - Add documentation
   - Create usage examples

## Design Principles to Apply

1. **Single Responsibility Principle**:
   - Each class should have only one reason to change
   - Services should handle business logic, clients handle API interaction

2. **Open/Closed Principle**:
   - Design for extension without modification
   - Use plugin architecture for new tool types

3. **Composition Over Inheritance**:
   - Use service composition instead of inheritance hierarchies
   - Prefer decorators and functional patterns

4. **Dependency Inversion Principle**:
   - Depend on abstractions, not concrete implementations
   - Use dependency injection for services

5. **Don't Repeat Yourself (DRY)**:
   - Eliminate duplication in tool registration and execution
   - Use FastMCP's built-in capabilities rather than reimplementing them

## Project Structure

```
src/
├── __init__.py
├── config.py            # Configuration management
├── server.py            # Main FastMCP server implementation
├── services/            # Domain services layer
│   ├── __init__.py
│   ├── issue.py         # Issue-related business logic
│   ├── project.py       # Project-related business logic
│   └── user.py          # User-related business logic
├── client.py            # Redmine API client
└── resources/           # FastMCP resource definitions
    ├── __init__.py
    ├── issue.py         # Issue resource definitions
    └── project.py       # Project resource definitions
```

## Testing Strategy

1. **Unit Tests**:
   - Test each service in isolation
   - Mock the API client for service tests
   - Test error handling paths

2. **Integration Tests**:
   - Test the integration between services and the API client
   - Use a test Redmine instance

3. **End-to-End Tests**:
   - Test the complete FastMCP server
   - Simulate client requests and validate responses

## Monitoring and Continuous Improvement

1. Implement code complexity metrics in CI pipeline
2. Regularly review and refactor based on metrics
3. Conduct regular design reviews against the principles
4. Gather feedback from users and contributors
5. Track improvements against the defined metrics

## Conclusion

This architecture focuses on leveraging FastMCP's native capabilities while maintaining a clean, simple design that fights complexity. By adhering to established software design principles and measurable success criteria, the rrmcpy project can provide a robust, maintainable interface to Redmica that's easy for developers to use and extend.
