# Error Handling and Logging Guide

This guide documents the standardized error handling and logging system implemented for issues #117 and #124.

## Overview

The Redmine MCP Server now features:
- **Consistent error response format** across all operations
- **Structured logging** with context-aware information
- **Error code standardization** for better debugging
- **Component-based logging** for filtering and analysis

## Error Handling (Issue #117)

### Standard Error Format

All errors follow this consistent structure:

```json
{
  "error": true,
  "error_code": "ERROR_CODE",
  "message": "Human readable error message",
  "status_code": 400,
  "timestamp": "2025-06-04T23:00:00.000Z",
  "details": {
    // Optional: Additional error details
  },
  "context": {
    // Optional: Request context
  }
}
```

### Error Codes

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Invalid input data |
| `AUTHENTICATION_ERROR` | 401 | Invalid API key |
| `AUTHORIZATION_ERROR` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `CONFLICT` | 409 | Resource conflict |
| `RATE_LIMIT` | 429 | Rate limit exceeded |
| `CONNECTION_ERROR` | 503 | Cannot connect to server |
| `TIMEOUT_ERROR` | 504 | Request timeout |
| `SERVER_ERROR` | 500 | Server error |
| `UNEXPECTED_ERROR` | 500 | Unexpected error |

### Usage Examples

```python
from src.core.errors import ErrorResponse, ErrorCode, validation_error

# Create a validation error
error = validation_error(
    "Missing required fields",
    field_errors={"name": "This field is required"},
    context={"provided_fields": ["description"]}
)

# Create a custom error
error = ErrorResponse.create(
    ErrorCode.NOT_FOUND,
    "Project not found",
    404,
    details={"project_id": "test-123"}
)
```

## Logging System (Issue #124)

### Configuration

Configure logging via environment variables:

```bash
# Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Enable structured logging (true/false)
LOG_STRUCTURED=true

# Include extra context (true/false)
LOG_CONTEXT=true

# Filter by components (comma-separated)
LOG_COMPONENTS=issues,projects
```

### Structured Logging Format

In production (INFO level and above), logs are output as JSON:

```json
{
  "timestamp": "2025-06-04T23:00:00.000Z",
  "level": "ERROR",
  "logger": "redmine_mcp_server.issues",
  "message": "Validation error: Missing required fields",
  "location": {
    "file": "issues.py",
    "line": 82,
    "function": "create_issue"
  },
  "context": {
    "error_code": "VALIDATION_ERROR",
    "field_errors": {"project_id": "This field is required"}
  }
}
```

In development (DEBUG level), logs use a readable format:
```
2025-06-04 23:00:00 - redmine_mcp_server.issues - ERROR - Validation error: Missing required fields
```

### Logging Best Practices

1. **Use component-specific loggers:**
   ```python
   from src.core.logging import get_logger
   logger = get_logger(__name__)
   ```

2. **Log API requests with context:**
   ```python
   from src.core.logging import log_api_request
   
   log_api_request(
       logger,
       method="GET",
       url="https://api.example.com/data",
       duration_ms=123.45,
       status_code=200
   )
   ```

3. **Log errors with full context:**
   ```python
   from src.core.logging import log_error_with_context
   
   try:
       # operation
   except Exception as e:
       log_error_with_context(
           logger,
           e,
           operation="create_issue",
           issue_data=data
       )
   ```

## Integration Example

Here's how error handling and logging work together:

```python
from src.base import RedmineBaseClient
from src.core.logging import get_logger

class IssueClient(RedmineBaseClient):
    def __init__(self, base_url: str, api_key: str):
        super().__init__(base_url, api_key)
        self.logger = get_logger("issues")
    
    def create_issue(self, data: Dict) -> Dict:
        # Validation with error handling
        if not data.get("subject"):
            return self.error_handler.handle_validation_error(
                "Issue subject cannot be empty",
                field_errors={"subject": "This field is required"},
                context={"data": data}
            )
        
        # API request with logging
        result = self.make_request("POST", "issues.json", data={"issue": data})
        
        # Errors are automatically logged and formatted
        return result
```

## Testing

Run the test suite to verify error handling and logging:

```bash
# Run all tests
pytest tests/test_error_and_logging.py -v

# Run in Docker
docker run --rm \
  -e REDMINE_URL="$REDMINE_URL" \
  -e REDMINE_API_KEY="$REDMINE_API_KEY" \
  -e LOG_LEVEL="DEBUG" \
  redmine-mcp-server:test \
  python -m pytest tests/test_error_and_logging.py -v
```

## Benefits

1. **Consistent Error Handling**: All errors follow the same format, making debugging easier
2. **Better Observability**: Structured logs can be easily parsed and analyzed
3. **Context-Rich Debugging**: Errors include relevant context and details
4. **Component Filtering**: Log only what you need to see
5. **Production-Ready**: Structured logging works well with log aggregation tools

## Migration Notes

If you have existing code using the old error format:

```python
# Old way
return {"error": "Something went wrong"}

# New way
from src.core.errors import unexpected_error
return unexpected_error(Exception("Something went wrong"))
```

The system maintains backward compatibility with legacy error classes while encouraging use of the new standardized approach.
