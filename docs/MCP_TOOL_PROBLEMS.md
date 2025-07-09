# Redmine MCP Tool Problems Documentation

## Overview
This document captures all problems discovered with the Redmine MCP tools during testing on July 9, 2025. These issues were found by actually using the tools through Claude's interface.

## Critical Issues

### 1. Parameter Validation Problems
**Issues:** #649, #681, #682
- **Problem**: Standard Redmine API parameters are rejected
- **Examples**:
  - `parent_issue_id` not accepted in create_issue
  - `done_ratio` not accepted in update_issue
  - Template placeholders (FEATURE_NAME, etc.) rejected
- **Impact**: Cannot use basic Redmine functionality through MCP

### 2. Wiki Creation Bug
**Issue:** #687 (related to #659)
- **Problem**: `redmine-create-wiki-page` fails with "Failed to create wiki page: True"
- **Workaround**: Use `redmine-update-wiki-page` which creates pages
- **Impact**: Confusing user experience, inconsistent behavior

### 3. Content Length Restrictions
**Issue:** #688
- **Problem**: 403 Forbidden errors with long content
- **Examples**:
  - Cannot update issues with detailed descriptions
  - Cannot create wiki pages with extensive documentation
- **Impact**: Must break up content into multiple operations

### 4. Unhelpful Error Messages
**Issue:** #689
- **Problem**: Errors show Pydantic URLs instead of helpful context
- **Missing**:
  - List of valid parameters
  - Examples of correct usage
  - Explanation of why parameter was rejected
- **Impact**: Poor developer experience, time wasted debugging

### 5. Documentation Out of Sync
**Issue:** #683
- **Problem**: 29 tools available but only 17 documented
- **Missing Documentation**:
  - Wiki Management (5 tools)
  - Template System (4 tools)
  - Additional Project tools (3 tools)
- **Impact**: Users unaware of available functionality

## Test Results

### Parameters That Should Work But Don't
```python
# These all fail with "Unexpected keyword argument"
redmine-create-issue(
    parent_issue_id=123,     # FAILS
    done_ratio=50,           # FAILS  
    start_date="2025-07-09", # FAILS
    estimated_hours=8.0      # FAILS
)

redmine-update-issue(
    issue_id=123,
    done_ratio=75  # FAILS
)
```

### Wiki Operations
```python
# This fails
redmine-create-wiki-page(
    project_id="rrmcpy",
    page_name="Test",
    text="Content"
)
# Error: "Failed to create wiki page: True"

# This works (but shouldn't create)
redmine-update-wiki-page(
    project_id="rrmcpy",
    page_name="Test", 
    text="Content"
)
```

### Content Length Issues
```python
# Short content works
redmine-create-issue(
    project_id="rrmcpy",
    subject="Test",
    description="Short"  # OK
)

# Long content fails
redmine-update-issue(
    issue_id=123,
    description="[2000+ chars]"  # 403 Forbidden
)
```

## Common Error Patterns

1. **Vague Errors**: "True" or HTML responses instead of messages
2. **Missing Context**: No indication of valid parameters
3. **Inconsistent Behavior**: Update doing create operations
4. **Silent Failures**: Some operations appear to work but don't

## Roadmap Alignment

Per `/docs/ROADMAP.md`, these issues should be addressed in:
- **v0.9.0** - Critical bug fixes (parameter validation)
- **v1.0.0** - Architecture simplification
- **v1.1.0** - Complete tool implementation

## Recommendations

### Immediate (v0.9.0)
1. Add all standard Redmine parameters to tool definitions
2. Fix wiki creation bug
3. Improve error messages with parameter lists

### Short Term
1. Document or remove content length restrictions
2. Update architecture.md with all 29 tools
3. Add integration tests for all parameters

### Long Term
1. Dynamic parameter discovery from Redmine API
2. Better error handling with examples
3. Comprehensive documentation generation

## Related Issues
- #690: Meta-issue tracking all tool problems
- #685: DevOps workflow for fixing these issues
- #686: Session summary of findings

## Testing Instructions

To reproduce these issues:
1. Use the MCP tools through Claude
2. Try standard Redmine parameters
3. Attempt wiki operations
4. Test with long content

All issues are reproducible and affect real usage.
