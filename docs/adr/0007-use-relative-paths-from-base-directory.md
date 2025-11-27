# 7. Use relative paths from base directory

Date: 2025-11-28

## Status

Accepted

## Context

We needed to decide how to represent file paths in query results.

Candidates:
- Absolute path: `/Users/kzmshx/Documents/Obsidian/atoms/daily/2025-11-01.md`
- Relative path: `daily/2025-11-01.md`

## Decision

Use relative paths from `--base-dir`.

```python
result["path"] = str(path.relative_to(base_dir))
```

## Consequences

- Portable path representation independent of environment
- Concise output with unnecessary prefixes removed
- Paths outside base-dir are not included in results
- Clients need to join with base-dir if absolute paths are required
