#!/usr/bin/env python3
"""
Quick reference for MCP tool issues and their fixes
Run this to see current issue status and fix guidelines
"""

TOOL_ISSUES = {
    "Parameter Validation": {
        "issues": ["#649", "#681", "#682"],
        "problems": [
            "parent_issue_id not accepted in create_issue",
            "done_ratio not accepted in update_issue", 
            "Template placeholders rejected",
            "Missing: start_date, due_date, estimated_hours, etc."
        ],
        "fix_location": "src/tools/issue_tools.py",
        "fix_approach": "Add missing parameters to tool definitions"
    },
    
    "Wiki Creation": {
        "issues": ["#687"],
        "problems": [
            "create_wiki_page fails with 'True' error",
            "update_wiki_page creates pages (inconsistent)"
        ],
        "fix_location": "src/tools/wiki_tools.py", 
        "fix_approach": "Check API response handling for wiki creation"
    },
    
    "Content Length": {
        "issues": ["#688"],
        "problems": [
            "403 Forbidden with long descriptions",
            "No clear error about limits"
        ],
        "fix_location": "src/api/base.py or server config",
        "fix_approach": "Check request size limits, improve error messages"
    },
    
    "Error Messages": {
        "issues": ["#689"],
        "problems": [
            "Pydantic URLs instead of help",
            "No list of valid parameters",
            "No usage examples"
        ],
        "fix_location": "src/tools/base_tool.py",
        "fix_approach": "Override error handling to provide better messages"
    },
    
    "Documentation": {
        "issues": ["#683"],
        "problems": [
            "29 tools exist, 17 documented",
            "Wiki tools undocumented",
            "Template tools undocumented"
        ],
        "fix_location": "docs/architecture.md",
        "fix_approach": "Update documentation to match reality"
    }
}

def print_issue_summary():
    """Print a summary of all tool issues"""
    print("🔧 Redmine MCP Tool Issues Quick Reference")
    print("=" * 60)
    
    for category, info in TOOL_ISSUES.items():
        print(f"\n📌 {category}")
        print(f"   Issues: {', '.join(info['issues'])}")
        print(f"   Fix in: {info['fix_location']}")
        print("   Problems:")
        for problem in info['problems']:
            print(f"     - {problem}")
        print(f"   Approach: {info['fix_approach']}")
    
    print("\n" + "=" * 60)
    print("Use DevOps workflow: ./scripts/start-issue.sh <issue-id>")
    print("Test after fixes: ./scripts/test-tool.sh <tool-name>")

if __name__ == "__main__":
    print_issue_summary()
