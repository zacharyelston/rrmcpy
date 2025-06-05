# Interactive MCP Testing Client - Design Document

## Overview
The Interactive MCP Testing Client is a command-line tool that provides a REPL (Read-Eval-Print Loop) interface for testing and debugging MCP (Model Context Protocol) servers. It dramatically improves the developer experience by providing immediate feedback, session management, and debugging capabilities.

## Version Target: 1.0.0

### Release Goals
- Production-ready interactive client for MCP protocol testing
- Full compatibility with FastMCP-based servers
- Comprehensive documentation and examples
- Cross-platform support (Linux, macOS, Windows)

## Architecture

### Core Components

```
mcp_client/
├── __init__.py
├── cli.py              # Main CLI entry point
├── client.py           # MCP client implementation
├── repl.py            # Interactive REPL logic
├── templates.py       # Template management
├── session.py         # Session recording/playback
├── formatter.py       # Output formatting
├── completer.py       # Tab completion logic
└── utils.py           # Utility functions
```

### Key Classes

```python
class MCPTestClient:
    """Main client for MCP communication"""
    def __init__(self, server_cmd: Optional[str] = None)
    async def connect(self) -> None
    async def call_tool(self, name: str, args: Dict) -> Dict
    async def list_tools(self) -> List[Dict]
    
class InteractiveREPL:
    """Interactive REPL interface"""
    def __init__(self, client: MCPTestClient)
    async def run(self) -> None
    def parse_command(self, line: str) -> Command
    
class SessionRecorder:
    """Record and replay sessions"""
    def start_recording(self) -> None
    def stop_recording(self, filename: str) -> None
    async def replay(self, filename: str) -> None
    
class TemplateManager:
    """Manage request templates"""
    def save_template(self, name: str, request: Dict) -> None
    def load_template(self, name: str) -> Dict
    def list_templates(self) -> List[str]
```

## Features

### Phase 1: Core Functionality (v0.1.0)
- [x] Basic REPL interface
- [x] JSON-RPC communication over stdio
- [x] Tool invocation with arguments
- [x] Pretty-printed JSON responses
- [x] Error handling and display
- [x] Command history (using readline)

### Phase 2: Enhanced Features (v0.5.0)
- [ ] Tab completion for tool names and parameters
- [ ] Template management (save/load/list)
- [ ] Debug mode with request/response logging
- [ ] Session recording and playback
- [ ] Batch command execution
- [ ] Export session to markdown/JSON

### Phase 3: Advanced Features (v1.0.0)
- [ ] Multiple server support (switch between servers)
- [ ] Plugin system for custom formatters
- [ ] Performance metrics (timing, memory)
- [ ] Integration test suite generation
- [ ] Web UI companion (optional)
- [ ] Docker container support

## Command Reference

### Basic Commands
```bash
# Tool operations
call <tool-name> [param=value ...]   # Call an MCP tool
list-tools                           # List available tools
help <tool-name>                     # Show tool documentation

# Session management
record start                         # Start recording session
record stop <filename>               # Stop and save recording
replay <filename>                    # Replay a session

# Template management
save-template <name>                 # Save last request as template
load-template <name>                 # Load a template
list-templates                       # Show available templates
edit-template <name>                 # Edit template in editor

# Utility commands
debug on|off                         # Toggle debug mode
format json|yaml|table               # Set output format
export <filename>                    # Export session
clear                               # Clear screen
exit                                # Exit client
```

### Advanced Usage
```bash
# Batch execution
batch start
batch> call redmine-create-issue project_id=test subject="Issue 1"
batch> call redmine-create-issue project_id=test subject="Issue 2"
batch run

# Scripting mode
mcp_client --script commands.txt
mcp_client --eval 'call redmine-list-issues project_id=test'

# Server management
connect <server-command>
disconnect
status
```

## Implementation Timeline

### Milestone 1: Basic REPL (2 weeks)
- Set up project structure
- Implement basic REPL loop
- Add JSON-RPC communication
- Create call command
- Add error handling

### Milestone 2: Developer Experience (2 weeks)
- Add tab completion
- Implement template system
- Add debug mode
- Create help system
- Improve output formatting

### Milestone 3: Advanced Features (3 weeks)
- Session recording/playback
- Batch execution
- Performance metrics
- Test generation
- Documentation

### Milestone 4: Polish & Release (1 week)
- Cross-platform testing
- Performance optimization
- Documentation completion
- Example scripts
- Release preparation

## Usage Examples

### Basic Tool Testing
```bash
$ mcp_client
Connected to Redmine MCP Server v0.9.0

MCP> list-tools
Available tools:
  redmine-create-issue     Create a new issue in Redmine
  redmine-update-issue     Update an existing issue
  redmine-list-issues      List issues with optional filters
  ...

MCP> call redmine-create-issue project_id=rrmcpy subject="Test issue" description="Testing the client"
{
  "issue": {
    "id": 150,
    "project": {"id": 6, "name": "rrmcpy"},
    "subject": "Test issue",
    "description": "Testing the client",
    "created_on": "2025-06-05T01:00:00Z"
  }
}
```

### Debugging Protocol Issues
```bash
MCP> debug on
Debug mode enabled

MCP> call redmine-update-issue issue_id=999 subject="Updated"
[DEBUG] Request:
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "id": "1234",
  "params": {
    "name": "redmine-update-issue",
    "arguments": {
      "issue_id": 999,
      "subject": "Updated"
    }
  }
}

[DEBUG] Response:
{
  "jsonrpc": "2.0",
  "id": "1234",
  "error": {
    "code": -32001,
    "message": "Tool error",
    "data": {
      "error": "NOT_FOUND",
      "message": "Issue 999 not found"
    }
  }
}
```

### Template Usage
```bash
MCP> call redmine-create-issue project_id=test subject="Bug report" tracker_id=1 priority_id=4
{ ... success ... }

MCP> save-template bug-report
Template 'bug-report' saved

MCP> load-template bug-report
Loaded template: redmine-create-issue project_id=test subject="Bug report" tracker_id=1 priority_id=4

MCP> # Edit the subject and create another
MCP> call redmine-create-issue project_id=test subject="Another bug" tracker_id=1 priority_id=4
```

## Testing Strategy

### Unit Tests
- Command parsing
- Template management
- Session recording
- Output formatting

### Integration Tests
- Full REPL flow
- Server communication
- Error handling
- Performance benchmarks

### End-to-End Tests
- Complete user workflows
- Cross-platform compatibility
- Stress testing

## Security Considerations

1. **Credential Management**
   - Never log API keys or sensitive data
   - Mask credentials in debug output
   - Secure template storage

2. **Input Validation**
   - Sanitize user input
   - Prevent injection attacks
   - Validate JSON-RPC responses

3. **File Operations**
   - Restrict file access to designated directories
   - Validate file paths
   - Check file permissions

## Performance Requirements

- Startup time: < 500ms
- Command response: < 100ms (excluding server processing)
- Memory usage: < 50MB base, < 100MB with history
- Support for sessions with 10,000+ commands

## Dependencies

```toml
[dependencies]
click = "^8.1.0"          # CLI framework
prompt_toolkit = "^3.0"   # Advanced REPL features
rich = "^13.0"           # Pretty printing
aiohttp = "^3.9"         # Async HTTP (future)
pydantic = "^2.0"        # Data validation
```

## Future Enhancements

1. **Web UI Dashboard**
   - Real-time session view
   - Visual tool explorer
   - Shareable sessions

2. **Plugin System**
   - Custom commands
   - Output transformers
   - Protocol extensions

3. **AI Integration**
   - Natural language to MCP commands
   - Intelligent error suggestions
   - Pattern detection

## Success Metrics

- Developer adoption rate > 80%
- Average time to first successful tool call < 2 minutes
- Session recording used in > 50% of bug reports
- Documentation examples generated from real sessions

## Conclusion

The Interactive MCP Testing Client will transform the MCP development experience from a compile-test-debug cycle to an interactive exploration process. By providing immediate feedback, session management, and powerful debugging tools, it will significantly reduce development time and improve code quality.
