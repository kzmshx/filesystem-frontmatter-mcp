# 6. JSON encode arrays

Date: 2025-11-28

## Status

Accepted

## Context

We needed to decide how to handle frontmatter arrays (e.g., `tags: [ai, python]`) in DuckDB.

Since ADR-0005 established treating all values as strings, arrays also needed some string representation.

## Decision

Arrays are JSON-encoded as strings, and expanded on the SQL side using `from_json()` and `UNNEST`.

```python
# Python side
if isinstance(value, list):
    return json.dumps(value, ensure_ascii=False)
```

```sql
-- SQL side expansion
SELECT path, tag
FROM files, UNNEST(from_json(tags, '[""]')) AS t(tag)
```

## Consequences

- Consistent with ADR-0005's all-strings approach
- All columns unified as string type
- Arrays can be dynamically converted using DuckDB's `from_json()` function
- `from_json()` requires a schema hint as the second argument (`'[""]'`)
