# 3. Use DuckDB for SQL queries

Date: 2025-11-28

## Status

Accepted

## Context

We needed to decide how to filter and aggregate frontmatter data.

Candidates:
- pandas: Higher learning curve than SQL, difficult to use from MCP clients
- SQLite: Weak array operations, limited JSON function support
- jq-style DSL: High implementation cost, also requires learning
- DuckDB: Expressive SQL, array operations, in-memory execution

## Decision

Adopted DuckDB as the in-memory SQL engine.

## Consequences

- Complex queries possible with WHERE, GROUP BY, JOIN, etc.
- Easy array expansion with `UNNEST` and `from_json()`
- Fast in-memory execution
- No server process required, embeddable as a Python library
- Depends on DuckDB's SQL dialect
