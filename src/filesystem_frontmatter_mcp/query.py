"""DuckDB query execution module."""

from typing import Any

import duckdb
import pyarrow as pa


def execute_query(records: list[dict[str, Any]], sql: str) -> dict[str, Any]:
    """Execute DuckDB SQL query on frontmatter records.

    Args:
        records: List of parsed frontmatter records.
        sql: SQL query string. Must reference 'files' table.

    Returns:
        Dictionary with results, row_count, and columns.
    """
    if not records:
        # Handle empty records case
        return {
            "results": [],
            "row_count": 0,
            "columns": [],
        }

    # Convert records to pyarrow Table
    # First, collect all unique keys across all records
    all_keys: set[str] = set()
    for record in records:
        all_keys.update(record.keys())

    # Build columns dict with None for missing keys
    columns_data: dict[str, list[Any]] = {key: [] for key in all_keys}
    for record in records:
        for key in all_keys:
            columns_data[key].append(record.get(key))

    # Create pyarrow table
    table = pa.table(columns_data)

    # Create connection and register table
    conn = duckdb.connect(":memory:")
    conn.register("files", table)

    # Execute query
    result = conn.execute(sql)
    columns = [desc[0] for desc in result.description]
    rows = result.fetchall()

    # Convert to list of dicts
    results = [dict(zip(columns, row, strict=True)) for row in rows]

    return {
        "results": results,
        "row_count": len(results),
        "columns": columns,
    }
