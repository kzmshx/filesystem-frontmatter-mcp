"""Frontmatter parser module."""

from pathlib import Path
from typing import Any

import frontmatter


def parse_file(path: Path, base_dir: Path) -> dict[str, Any]:
    """Parse frontmatter from a single file.

    Args:
        path: Absolute path to the file.
        base_dir: Base directory for relative path calculation.

    Returns:
        Dictionary with 'path' (relative) and frontmatter properties.
    """
    post = frontmatter.load(path)
    result: dict[str, Any] = {
        "path": str(path.relative_to(base_dir)),
    }
    result.update(post.metadata)
    return result


def parse_files(
    paths: list[Path], base_dir: Path
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    """Parse frontmatter from multiple files.

    Args:
        paths: List of absolute paths to files.
        base_dir: Base directory for relative path calculation.

    Returns:
        Tuple of (parsed records, warnings for failed files).
    """
    records: list[dict[str, Any]] = []
    warnings: list[dict[str, str]] = []

    for path in paths:
        try:
            record = parse_file(path, base_dir)
            records.append(record)
        except Exception as e:
            warnings.append(
                {
                    "path": str(path.relative_to(base_dir)),
                    "error": str(e),
                }
            )

    return records, warnings


def infer_schema(
    records: list[dict[str, Any]], max_samples: int = 5
) -> dict[str, dict[str, Any]]:
    """Collect schema information from parsed records.

    Note: This does not perform type inference. All values are treated
    as strings in DuckDB queries. This function provides metadata about
    what properties exist and their sample values.

    Args:
        records: List of parsed frontmatter records.
        max_samples: Maximum number of sample values to include.

    Returns:
        Schema dict with count, nullable, sample_values for each property.
    """
    schema: dict[str, dict[str, Any]] = {}
    property_values: dict[str, list[Any]] = {}

    for record in records:
        for key, value in record.items():
            if key == "path":
                continue
            if key not in property_values:
                property_values[key] = []
            property_values[key].append(value)

    total_files = len(records)

    for prop, values in property_values.items():
        non_null_values = [v for v in values if v is not None]
        count = len(non_null_values)

        # Detect if values are arrays
        is_array = any(isinstance(v, list) for v in non_null_values)

        # Collect unique sample values
        seen: set[str] = set()
        samples: list[Any] = []
        for v in non_null_values:
            key = str(v)
            if key not in seen and len(samples) < max_samples:
                seen.add(key)
                samples.append(v)

        schema[prop] = {
            "type": "array" if is_array else "string",
            "count": count,
            "nullable": count < total_files,
            "sample_values": samples,
        }

    return schema
