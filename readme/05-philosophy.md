# Design Principle: Keep It Simple

The Redmine MCP Server is built around one goal: make things simpler, not harder.

Every design and code decision is made to reduce confusion and complexity. We believe that the hardest part of software isn't adding features—it's keeping everything understandable as it grows.

## How We Keep Things Simple

### Simple > Clever
- Clear, obvious solutions are better than smart ones that are hard to follow
- Use straightforward code that anyone can understand and maintain
- Avoid unnecessary abstractions that obscure what the code actually does

### Small Pieces
- Each part of the system does one thing well
- Modules like `ClientManager` or `ServiceManager` can be worked on without needing to know the whole system
- Build complex functionality from simple, well-defined components

### Hide the Mess
- Keep implementation details behind clean, easy-to-use interfaces
- Separate what something does from how it does it
- Design clear APIs between system components

### Stick to the Basics
- Follow proven design rules:
  - **SOLID**: Design patterns that lead to maintainable code
  - **KISS**: Keep It Simple, Stupid
  - **DRY**: Don't Repeat Yourself
  - **YAGNI**: You Aren't Gonna Need It (avoid overengineering)

### Always Improving
- Continuously refine the system—less clutter, better code, every time we touch it
- Remove complexity whenever possible
- Evolve the system based on real-world use, not theoretical needs

## Why Simplicity Matters

Simple systems are:
- **Faster to build**: Less time spent on unnecessary complexity
- **Easier to fix**: Problems are more isolated and understandable
- **Nicer to use**: Both for developers and end-users
- **More maintainable**: New team members can get up to speed quickly
- **More reliable**: Fewer moving parts means fewer things that can break

That's what Redmine MCP is all about—powerful functionality without the complexity.