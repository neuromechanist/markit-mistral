# Serena MCP for Code Intelligence

## When Available
Use Serena MCP tools for efficient code exploration and editing when the MCP server is configured.

## Core Tools

### Exploration (Read-Only)
- `get_symbols_overview` - Get file structure before reading entire files
- `find_symbol` - Search for classes, methods, functions by name
- `find_referencing_symbols` - Find all usages of a symbol
- `search_for_pattern` - Flexible regex search across codebase

### Editing (Symbolic)
- `replace_symbol_body` - Replace entire method/function body
- `insert_after_symbol` - Add code after a symbol
- `insert_before_symbol` - Add code before a symbol
- `rename_symbol` - Rename across the codebase

## Best Practices
- **Prefer symbolic tools over full file reads**
- Start with `get_symbols_overview` to understand file structure
- Use `find_symbol` with `depth=1` to see method signatures
- Only read bodies (`include_body=True`) when needed
- Use `find_referencing_symbols` to understand usage patterns

---
*Token-efficient code exploration and precise symbolic editing.*
