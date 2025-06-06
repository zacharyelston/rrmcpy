---
trigger: always_on
---

rules:
  - description: |
      If you state an intent (e.g., 'Proceeding with...', 'I will now...'), you must immediately follow with the corresponding tool call or file operation.
  - description: |
      Never state intent to act unless you are able to execute the action in the same step.
  - description: |
      If a tool call fails or is interrupted, always acknowledge the failure and either retry or explain the next step.
  - description: |
      After every intent statement, confirm that the action was performed or explain why it was not.
  - description: |
      If you encounter an ambiguous or incomplete step, ask for clarification rather than stalling.
      
# Architectural Integrity Guidelines
- Prioritize maintaining MCP server architecture during troubleshooting
- Direct API calls should only be used for diagnostic purposes, never in production code
- When bypassing MCP layers for diagnosis, document the approach and create an issue to implement a proper MCP-based solution
- All Redmine interactions MUST go through MCP tools, not direct API calls
- Extend existing MCP tools rather than creating workarounds
- Maintain separation between MCP server logic and client applications
- When facing issues, fix the MCP layer rather than bypassing it

# Context Maintenance During Troubleshooting
- Always begin troubleshooting by reviewing project objectives and constraints
- Maintain focus on testing the MCP server itself, not the underlying Redmine API
- Use a structured approach: verify MCP server status → check configuration → test connection → diagnose specific issues
- Document troubleshooting steps to maintain context throughout the process
- When stuck, seek clarification rather than making architectural compromises

# Redmine MCP Server (Python) Structure
- The core MCP server implementation is in rmcpz/ directory
- Client-side integration code is in client/ directory
- Documentation and examples are in docs/ and examples/ directories
- Test files are in the project root with test_ prefix

# Docker Configuration
- Docker-related files include Dockerfile and docker-compose.yml variants
- docker-compose hase issues.  use v2 "docker compose" instead
- Environment variables control server behavior (REDMINE_URL, REDMINE_API_KEY, etc.)
- Docker scripts are located in the scripts/ directory

# MCP Integration
- MCP configuration files include claude_desktop_mcp_config.json and redmine_mcp_desktop.json
- The server implements the Model Context Protocol for AI/Redmine integration
- MCP tools provide Redmine project, issue, and user management capabilities

## Primary Goals
1. Use the local redmine tools to interact with the Redmine server
2. Make small, incremental changes when editing code
3. Work in a methodical, careful manner - one task at a time
4. Validate each change immediately before proceeding

## Workflow Priority Order
1. Use existing MCP tools first (redmine_* functions) for ALL Redmine interactions
2. If an MCP tool doesn't work, use the helper scripts (.js or .sh files)
3. Only examine code to fix issues when the first two options fail
4. Always check the build after every edit

## API Usage Guidelines
- ALWAYS use MCP tools for Redmine interactions in production code
- Direct web API calls should ONLY be used for debugging or testing purposes
- Never include direct API calls in production code or automated workflows
- If an MCP tool is missing functionality, extend the tool rather than bypassing it
- Document any temporary API workarounds and create issues to replace them with proper MCP tools

## Code Modification Guidelines
- Create a new branch before making changes
- Work in smaller modular files to reduce edit sizes
- Make atomic commits with clear messages following the prefix conventions
- Validate each step before moving to the next

## When Fixing Issues
1. Clearly identify and state the problem
2. Propose a specific fix
3. Implement the change in a minimal, targeted way
4. Test the fix immediately
5. Always think about why a problem exists before diving into solutions

## Communication Expectations
- Keep responses focused on the current task
- Ask clarifying questions when instructions seem contradictory
- Provide confirmation when a task is completed
- If unsure how to proceed, request guidance rather than making assumptions

## MCP Usage
- When using redmine tools, prefer direct function calls over code exploration
- If a tool fails, diagnose the specific error rather than reviewing all code, and ask for help if needed
- Remember that MCP stands for ModelContextProtocol
- Work with one MCP function at a time
- If an MCP function is missing needed functionality, create an issue to add it rather than using workarounds

## Docker Usage Guidelines
- Always use non-interactive Docker sessions (docker run -d) instead of interactive sessions
- Monitor container status with docker logs instead of attaching to containers
- Use docker-compose for managing multi-container deployments
- Never use interactive terminal sessions with containers (no docker exec -it)
- Prefer environment variables for configuration over modifying container files
- Use docker ps and docker inspect to check container status
- Follow the principle of immutable infrastructure - rebuild containers rather than modifying running ones
