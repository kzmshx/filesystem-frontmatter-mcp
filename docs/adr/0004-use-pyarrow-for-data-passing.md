# 4. Use PyArrow for data passing

Date: 2025-11-28

## Status

Accepted

## Context

We needed an efficient way to pass Python dict lists to DuckDB.

## Decision

Adopted passing data via PyArrow tables registered with DuckDB.

```python
schema = pa.schema([(key, pa.string()) for key in all_keys])
table = pa.table(columns_data, schema=schema)
conn.register("files", table)
```

## Consequences

- Column types can be explicitly specified with `pa.schema()`
- Arrow format is columnar and memory-efficient
- DuckDB natively supports Arrow format, minimizing conversion overhead
- Added dependency on pyarrow
