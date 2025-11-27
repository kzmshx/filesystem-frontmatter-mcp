# filesystem-frontmatter-mcp

An MCP server for querying Markdown frontmatter with DuckDB SQL.

## Features

- **inspect_frontmatter**: Get frontmatter schema from files matching a glob pattern
- **query_frontmatter**: Query frontmatter data with DuckDB SQL

## Installation

```bash
uv tool install git+https://github.com/kzmshx/filesystem-frontmatter-mcp.git
```

## Usage

### Configuration for Claude Desktop / Claude Code

```json
{
  "mcpServers": {
    "frontmatter": {
      "command": "filesystem-frontmatter-mcp",
      "args": ["--base-dir", "/path/to/markdown/directory"]
    }
  }
}
```

### Tool Examples

#### Inspect Schema

```
inspect_frontmatter("**/*.md")
```

Output example:

```json
{
  "file_count": 186,
  "schema": {
    "date": {
      "type": "string",
      "count": 180,
      "nullable": true,
      "sample_values": ["2025-11-01", "2025-11-02"]
    },
    "tags": {
      "type": "array",
      "count": 150,
      "nullable": true,
      "sample_values": [["ai", "claude"], ["python"]]
    }
  }
}
```

#### SQL Queries

```sql
-- List files from this month
SELECT path, date, tags
FROM files
WHERE date LIKE '2025-11-%'
ORDER BY date DESC

-- Aggregate tags (expanding arrays)
SELECT tag, COUNT(*) as count
FROM files, UNNEST(from_json(tags, '[""]')) AS t(tag)
WHERE date LIKE '2025-11-%'
GROUP BY tag
ORDER BY count DESC
```

## Technical Notes

### All Values Are Strings

All frontmatter values are passed to DuckDB as strings. Use `TRY_CAST` in SQL for type conversion when needed.

```sql
-- Date comparison
SELECT * FROM files
WHERE TRY_CAST(date AS DATE) >= '2025-11-01'
```

### Arrays Are JSON Strings

Arrays like `tags: [ai, python]` are stored as JSON strings `'["ai", "python"]'`. Use `from_json()` and `UNNEST` to expand them.

```sql
SELECT path, tag
FROM files, UNNEST(from_json(tags, '[""]')) AS t(tag)
WHERE tag = 'ai'
```

### Templater Expression Support

Files containing Obsidian Templater expressions (e.g., `<% tp.date.now("YYYY-MM-DD") %>`) are handled gracefully. These expressions are treated as strings and naturally excluded by date filtering.

## License

MIT
