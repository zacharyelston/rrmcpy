# Issue Reorganization Summary - Issues 427-463

## Quick Actions Required

### 1. Move Issues to Budget Project
Move issues 442-463 to the Budget project as they all relate to:
- Demo account implementation (442-446, 449-450)
- AWS infrastructure setup (444-445, 447)
- Plaid MCP integration (451-463)
- Development tools research (448)

### 2. Move Issue to Amplify-CLI-MCP Project
Move issue 427 as it's specifically about creating templates for the Amplify CLI MCP project.

### 3. Keep in rrmcpy Project
Issues 422-426 and 428-441 are correctly placed in rrmcpy.

## Consolidation Opportunities

### Template Creation Subtasks (423-426)
These four subtasks of issue 422 are very similar and could be consolidated into:
1. Research & Analysis (combining current 423)
2. Implementation & Testing (combining 424-425)
3. Documentation (keeping 426)

### Plaid MCP Documentation (460-463)
These documentation issues form a complete set and should be kept together, possibly as child issues of 460.

## Wiki Documentation Created

1. **Issue Reorganization Guide** - Complete mapping of all issues
2. **Budget Demo Account Guide** - Consolidates issues 442-446, 449-450
3. **Plaid MCP Integration Guide** - Consolidates issues 451-463

## Cross-Project Dependencies

- Redmine deployment (447) blocks demo testing
- AWS infrastructure (444-445) required for demo accounts
- Plaid MCP requires production Plaid access
- Demo accounts integrate with Cognito/LDAP (449-450)

## Recommended Next Steps

1. Manually move issues to correct projects in Redmine
2. Update parent-child relationships after moves
3. Add cross-references between related issues
4. Archive this reorganization guide for future reference