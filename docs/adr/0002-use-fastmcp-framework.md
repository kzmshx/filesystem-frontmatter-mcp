# 2. Use FastMCP framework

Date: 2025-11-28

## Status

Accepted

## Context

When implementing the MCP server in Python, we needed to choose how to define tools.

The initial implementation used manual tool schema definitions:

```python
TOOLS = [
    Tool(
        name="inspect_frontmatter",
        description="...",
        inputSchema={
            "type": "object",
            "properties": {
                "glob": {"type": "string", "description": "..."}
            },
            "required": ["glob"]
        }
    )
]
```

## Decision

Adopted FastMCP and migrated to decorator-based tool definitions.

```python
@mcp.tool()
def inspect_frontmatter(glob: str) -> str:
    """Get frontmatter schema from files matching glob pattern.

    Args:
        glob: Glob pattern relative to base directory.
    """
```

## Consequences

- Code reduced by approximately 50%
- Function definitions directly become tool definitions, with descriptions auto-generated from docstrings
- Schemas are auto-generated from type hints
- Added dependency on FastMCP
