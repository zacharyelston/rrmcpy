# Complete Project Restructure - Implementation Plan

## Objective
Complete refactoring of Redmine MCP Server to address code quality issues and implement tool registry pattern for better modularity, testability, and maintainability.

## Current Problems to Solve

### Code Quality Issues
1. **Mixed Abstraction Levels** - `redmine_client.py` acts as both facade and aggregator
2. **Inconsistent Error Handling** - Each module handles errors differently  
3. **Environment Variables Scattered** - Configuration spread across multiple files
4. **Monolithic Tool Registration** - All MCP tools defined in server class
5. **Hard to Test Individual Tools** - Tools coupled to server implementation

### Tool Registry Pattern Goals
- Decouple tool definitions from server implementation
- Enable individual tool testing in isolation
- Plugin-like architecture for extending functionality
- Clear separation between tool interface and business logic

## Phase 1: Foundation Restructure

### Step 1: Create New Directory Structure
```
src/
├── core/
│   ├── __init__.py
│   ├── config.py           # Centralized configuration management
│   ├── errors.py           # Standardized error handling
│   └── logging.py          # Logging configuration
├── services/
│   ├── __init__.py
│   ├── base_service.py     # Abstract base service
│   ├── issue_service.py    # Issue business logic
│   ├── project_service.py  # Project business logic
│   ├── user_service.py     # User business logic
│   └── group_service.py    # Group business logic
├── tools/
│   ├── __init__.py
│   ├── registry.py         # Tool registry implementation
│   ├── base_tool.py        # Abstract base tool
│   ├── issue_tools.py      # Issue-related MCP tools
│   ├── project_tools.py    # Project-related MCP tools
│   ├── admin_tools.py      # Administrative MCP tools
│   └── health_tools.py     # Health check tools
├── clients/
│   ├── __init__.py
│   ├── base_client.py      # Base API client (from current base.py)
│   ├── issue_client.py     # Issue API client (from current issues.py)
│   ├── project_client.py   # Project API client (from current projects.py)
│   ├── user_client.py      # User API client (from current users.py)
│   └── group_client.py     # Group API client (from current groups.py)
├── server/
│   ├── __init__.py
│   ├── mcp_server.py       # FastMCP server implementation
│   └── factory.py          # Server factory (future extensibility)
└── main.py                 # Application entry point
```

### Step 2: Core Infrastructure
- Extract configuration management from scattered environment variable usage
- Create standardized error classes and response formatting
- Implement centralized logging configuration

### Step 3: Service Layer Implementation
- Extract business logic from current API clients
- Implement validation, error handling, and business rules
- Create clean interfaces for tool layer consumption

### Step 4: Tool Registry System
- Create tool registry for dynamic tool registration
- Implement base tool interface with common functionality
- Separate tool definitions from server implementation

### Step 5: Client Layer Refactoring
- Clean up current API clients to focus only on HTTP communication
- Remove business logic and move to service layer
- Standardize response handling and error propagation

## Phase 2: Implementation Details

### Configuration Management (core/config.py)
```python
@dataclass
class RedmineConfig:
    url: str
    api_key: str
    timeout: int = 30
    max_retries: int = 3
    
    @classmethod
    def from_environment(cls) -> 'RedmineConfig':
        # Centralized env var handling
```

### Error Handling (core/errors.py)
```python
class RedmineAPIError(Exception):
    def __init__(self, message: str, status_code: int = None, details: dict = None):
        # Standardized error with context
        
class ToolExecutionError(Exception):
    # Tool-specific errors
```

### Base Tool Interface (tools/base_tool.py)
```python
from abc import ABC, abstractmethod

class BaseTool(ABC):
    @abstractmethod
    def name(self) -> str:
        pass
    
    @abstractmethod
    def description(self) -> str:
        pass
    
    @abstractmethod
    def input_schema(self) -> dict:
        pass
    
    @abstractmethod
    async def execute(self, **kwargs) -> dict:
        pass
```

### Tool Registry (tools/registry.py)
```python
class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
    
    def register(self, tool: BaseTool):
        self._tools[tool.name()] = tool
    
    def get_tool(self, name: str) -> BaseTool:
        return self._tools.get(name)
    
    def list_tools(self) -> List[dict]:
        # Return tool definitions for MCP
```

### Service Layer (services/issue_service.py)
```python
class IssueService:
    def __init__(self, client: IssueClient, config: RedmineConfig):
        self.client = client
        self.config = config
    
    def create_issue(self, data: dict) -> dict:
        # Validation, business logic, error handling
        validated_data = self._validate_create_data(data)
        result = self.client.create_issue(validated_data)
        return self._format_response(result)
```

## Phase 3: Migration Strategy

### Step 1: Create New Structure (No Breaking Changes)
- Create new directory structure alongside existing code
- Implement core infrastructure (config, errors, logging)
- No changes to existing functionality

### Step 2: Implement Service Layer
- Extract business logic from existing clients
- Create service classes with proper validation and error handling
- Test services independently

### Step 3: Build Tool Registry
- Implement tool registry and base tool interface
- Create individual tool classes using new service layer
- Test tools in isolation

### Step 4: Update Server Implementation
- Modify MCP server to use tool registry instead of monolithic tools
- Keep existing server working during transition
- Switch to new implementation once tested

### Step 5: Clean Up Legacy Code
- Remove old implementations once new system is verified
- Update documentation and examples
- Clean up unused imports and dependencies

## Testing Strategy

### Unit Testing
- Service layer testing with mocked clients
- Individual tool testing with mocked services
- Configuration validation testing

### Integration Testing
- End-to-end tool execution testing
- MCP protocol compliance testing
- Real Redmine API integration testing

### Migration Testing
- Parallel testing of old vs new implementations
- Regression testing to ensure no functionality loss
- Performance comparison testing

## Success Criteria

### Code Quality Improvements
- All configuration centralized in single location
- Consistent error handling across all modules
- Clear separation of concerns between layers
- Individual components testable in isolation

### Tool Registry Benefits
- Tools decoupled from server implementation
- Easy addition of new tools without server changes
- Plugin-like architecture for extensions
- Individual tool testing and validation

### Maintainability Gains
- Clear module boundaries and responsibilities
- Reduced code duplication
- Easier debugging and error tracking
- Better documentation and examples

## Timeline Estimate
- Phase 1: 2-3 days (foundation and structure)
- Phase 2: 3-4 days (implementation)
- Phase 3: 2-3 days (migration and testing)
- Total: 7-10 days for complete restructure

## Risk Mitigation
- Maintain existing functionality during transition
- Parallel implementation strategy to avoid breaking changes
- Comprehensive testing at each step
- Rollback plan if issues arise during migration