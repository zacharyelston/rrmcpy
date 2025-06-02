# Current Issues to Fix - Redmine MCP Server

## 🚨 Critical Issues Found During Testing

### 1. **Empty Response from create_issue Tool**
**Problem**: The `redmine_create_issue` MCP tool returns an empty dict `{}` instead of the created issue data, even though the underlying API works correctly.

**Root Cause**: The MCP server is correctly extracting the issue from the API response with `result.get('issue', {})`, but the data isn't being properly serialized/returned through the MCP protocol layer.

**Evidence**:
- Direct API test shows correct response with full issue data
- RedmineClient returns proper data structure
- MCP tool returns empty result to Claude

**Fix Required**:
- Debug the FastMCP response serialization
- Ensure the tool return type matches what FastMCP expects
- Check if there's an issue with the Pydantic model serialization

### 2. **List Operations Return Concatenated Objects**
**Problem**: The `redmine_list_issues` returns multiple issue objects concatenated together instead of a proper JSON array.

**Root Cause**: The MCP protocol may be incorrectly serializing List[Dict] responses.

**Evidence**:
- `redmine_list_issues` shows multiple JSON objects without array brackets
- Each object is complete but they're not in an array structure

**Fix Required**:
- Verify the return type annotation matches FastMCP expectations
- Check if FastMCP requires a specific format for list responses
- Test with explicit JSON serialization

### 3. **Tool Naming Conflicts** ✅ (Already Fixed)
According to TODO.md, tools have been renamed with `redmine_` prefix to avoid conflicts with GitHub MCP servers.

## 📋 Implementation Tasks

### Immediate Fixes Needed:

1. **Fix create_issue Response**
   ```python
   # Current implementation in proper_mcp_server.py
   @self.app.tool()
   def redmine_create_issue(request: IssueCreateRequest) -> Dict[str, Any]:
       # ... 
       return result.get('issue', {})  # This returns empty
   ```
   
   **Proposed Fix**:
   - Add debug logging to see what `result` contains
   - Ensure the response is properly awaited if async
   - Test with explicit dictionary construction
   - Check FastMCP serialization requirements

2. **Fix List Response Format**
   ```python
   @self.app.tool()
   def redmine_list_issues(...) -> List[Dict[str, Any]]:
       # ...
       return result.get('issues', [])  # Returns concatenated objects
   ```
   
   **Proposed Fix**:
   - Verify FastMCP's handling of List return types
   - Test with explicit JSON array serialization
   - Check if there's a FastMCP configuration for list responses

3. **Add Response Validation**
   - Add response validation before returning from tools
   - Log the actual response data for debugging
   - Add unit tests for response serialization

### Testing Requirements:

1. **Unit Tests for Response Handling**
   - Test that create_issue returns the created issue data
   - Test that list operations return proper JSON arrays
   - Test error response handling

2. **Integration Tests**
   - Test full workflow: create issue → get issue → verify data
   - Test pagination and filtering with list operations
   - Test error scenarios

3. **MCP Protocol Tests**
   - Test the actual MCP protocol responses
   - Verify JSON-RPC compliance
   - Test with different MCP clients

## 🔧 Technical Details from Implementation Plan

Based on `implementation_plan.md`, the following specifications should be met:

### Issues API Requirements:
- `createIssue` should return: `"object: created issue"`
- `listIssues` should return: `"Array<object>: issue summaries"`

### FastMCP Integration Requirements:
1. Tool decorators must be applied after MCP initialization ✅
2. All logging must go to stderr ✅
3. Proper error handling for FastMCP object properties
4. **All inputs/outputs should use explicit Pydantic models for proper serialization** ⚠️

## 🎯 Action Plan

1. **Debug Response Serialization** (Priority 1)
   - Add comprehensive logging to track response data flow
   - Test with different return type annotations
   - Verify Pydantic model serialization

2. **Fix List Response Format** (Priority 2)
   - Ensure proper JSON array serialization
   - Test with FastMCP's expected list format

3. **Add Response Validation** (Priority 3)
   - Implement response validation middleware
   - Add response logging for debugging

4. **Update Tests** (Priority 4)
   - Add specific tests for response formats
   - Test with actual MCP protocol

## 📝 Notes

- The underlying Redmine API integration is working correctly
- The issue is specifically in the MCP protocol layer
- FastMCP may have specific requirements for response serialization that aren't documented
- Consider checking FastMCP source code or examples for proper response handling