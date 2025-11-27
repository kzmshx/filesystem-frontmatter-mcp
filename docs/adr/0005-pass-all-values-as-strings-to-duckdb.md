# 5. Pass all values as strings to DuckDB

Date: 2025-11-28

## Status

Accepted

## Context

Frontmatter values can contain mixed types (strings, numbers, dates, arrays, Templater expressions, etc.).

Initially, we performed type inference on the Python side and mapped to appropriate DuckDB types. However, this caused issues with files containing Obsidian Templater plugin expressions (e.g., `<% tp.date.now("YYYY-MM-DD") %>`):

```
date column contains both "2025-11-01" and "<% tp.date.now(...) %>"
-> Type inference determines "date" type
-> Templater expression cannot be converted to DATE type, causing error
```

## Decision

Changed to pass all values as strings to DuckDB.

```python
def _serialize_value(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, list):
        return json.dumps(value, ensure_ascii=False)
    return str(value)
```

Use `TRY_CAST` in SQL for type conversion when needed.

## Consequences

- Avoids type inference failures
- Consistent behavior with all columns as strings
- Type conversion possible on SQL side as needed
- Templater expressions are preserved as strings and naturally excluded by date filtering
- `TRY_CAST` required for numeric comparisons, etc.
