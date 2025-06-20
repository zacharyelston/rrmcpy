# Architecture Overview

The Redmine MCP Server follows a clean, modular architecture designed for clarity and maintainability.

## System Design

### Core Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   MCP Client    │    │  FastMCP Server │    │ Redmine Instance│
│  (Claude, etc.) │◄──►│   (Python)      │◄──►│   (REST API)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Architecture Layers

#### 1. MCP Protocol Layer
- **FastMCP Framework**: Handles MCP protocol communication
- **Tool Registration**: Exposes Redmine operations as MCP tools
- **JSON-RPC**: Standard MCP communication protocol

#### 2. Application Layer
- **Tool Functions**: Individual MCP tool implementations
- **Parameter Validation**: Input validation and type checking
- **Error Handling**: Consistent error response formatting

#### 3. API Client Layer
- **HTTP Client**: Manages Redmine REST API communication
- **Authentication**: API key-based authentication
- **Connection Management**: Retry logic and health monitoring

#### 4. Data Layer
- **Redmine REST API**: External data source
- **JSON Processing**: Request/response serialization
- **Error Translation**: API errors to user-friendly messages

## Component Details

### FastMCP Server (`fastmcp_server.py`)
```python
# Clean, direct implementation following FastMCP patterns
mcp = FastMCP("Redmine MCP Server")

@mcp.tool()
async def redmine_create_issue(project_id: str, subject: str, ...) -> str:
    # Direct API call without abstraction layers
    result = issue_client.create_issue(issue_data)
    return json.dumps(result, indent=2)
```

### API Clients (`src/`)
- **Base Client**: Common HTTP functionality
- **Issue Client**: Issue-specific operations
- **Project Client**: Project management operations
- **User Client**: User and group management

### Configuration
- **Environment Variables**: Simple configuration approach
- **Validation**: Startup configuration checks
- **Health Monitoring**: Connection verification

## Data Flow

### Tool Execution Flow
1. **MCP Client** sends tool request via JSON-RPC
2. **FastMCP Server** receives and validates request
3. **Tool Function** processes parameters and validates input
4. **API Client** makes authenticated HTTP request to Redmine
5. **Redmine API** processes request and returns JSON response
6. **Tool Function** formats response and handles errors
7. **FastMCP Server** returns formatted response to client

### Error Handling Flow
1. **Network/HTTP Errors**: Caught by API client with retry logic
2. **Authentication Errors**: Clear error messages about API key issues
3. **Validation Errors**: Parameter validation with specific error details
4. **Redmine Errors**: API error translation to user-friendly messages

## Design Principles

### 1. Simplicity Over Complexity
- Direct FastMCP integration without custom abstractions
- Global client instances instead of dependency injection
- Simple error handling with descriptive strings

### 2. Authentic Data Integration
- All operations use real Redmine instances
- No mock or placeholder data in any component
- Comprehensive error handling for authentic API responses

### 3. MCP Protocol Compliance
- Standard FastMCP patterns and decorators
- Consistent JSON response formatting
- Proper error response structures

### 4. Container Compatibility
- Event loop conflict resolution for development environments
- nest_asyncio integration for Jupyter/VS Code compatibility
- Standard STDIO transport for MCP communication

## Comparison: Simple vs Complex Architecture

### Current Simple Implementation
```
fastmcp_server.py (210 lines)
├── FastMCP instance
├── Global client variables  
├── @mcp.tool() decorated functions
├── Direct API calls
└── Simple error handling
```

### Previous Complex Implementation
```
src/mcp_server.py (1000+ lines)
├── Custom tool registry
├── Service layer abstractions
├── Configuration management
├── Multiple inheritance hierarchies
└── Indirect tool execution
```

## Performance Characteristics

### Latency
- **Tool Execution**: 100-500ms (depends on Redmine server response)
- **Health Checks**: 50-200ms
- **Bulk Operations**: Linear scaling with item count

### Scalability
- **Concurrent Requests**: Limited by Redmine server capacity
- **Memory Usage**: Minimal - stateless operation model
- **Connection Pooling**: Single persistent connection per client

### Reliability
- **Retry Logic**: Automatic retry for transient failures
- **Health Monitoring**: Continuous connection verification
- **Error Recovery**: Graceful degradation for API failures

## Extension Points

### Adding New Tools
1. Create new `@mcp.tool()` decorated function
2. Implement parameter validation
3. Add API client method if needed
4. Include error handling patterns

### Custom Authentication
```python
# Extend base client for custom auth
class CustomAuthClient(IssueClient):
    def _get_headers(self):
        return {"Authorization": f"Bearer {self.token}"}
```

### Additional Entities
- Follow existing client patterns in `src/`
- Implement CRUD operations consistently
- Add comprehensive error handling
- Include proper documentation

## Security Architecture

### Authentication Flow
1. **API Key Storage**: Environment variables only
2. **Request Authentication**: X-Redmine-API-Key header
3. **Permission Validation**: Redmine server enforces access control
4. **Error Disclosure**: Minimal information in error responses

### Security Boundaries
- **Input Validation**: All user inputs validated before API calls
- **Output Sanitization**: JSON serialization prevents injection
- **Network Security**: HTTPS enforcement for production deployments