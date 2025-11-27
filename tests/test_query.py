"""Tests for DuckDB query module."""

from datetime import date

from filesystem_frontmatter_mcp.query import execute_query


class TestExecuteQuery:
    """Tests for execute_query function."""

    def test_select_all(self) -> None:
        """Select all columns from records."""
        records = [
            {"path": "a.md", "title": "Title A"},
            {"path": "b.md", "title": "Title B"},
        ]
        result = execute_query(records, "SELECT * FROM files")

        assert result["row_count"] == 2
        assert "path" in result["columns"]
        assert "title" in result["columns"]

    def test_select_specific_columns(self) -> None:
        """Select specific columns."""
        records = [
            {"path": "a.md", "title": "Title A", "date": date(2025, 11, 27)},
            {"path": "b.md", "title": "Title B", "date": date(2025, 11, 26)},
        ]
        result = execute_query(records, "SELECT path, title FROM files")

        assert result["columns"] == ["path", "title"]
        assert len(result["results"]) == 2

    def test_where_clause(self) -> None:
        """Filter records with WHERE clause."""
        records = [
            {"path": "a.md", "date": date(2025, 11, 27)},
            {"path": "b.md", "date": date(2025, 11, 26)},
            {"path": "c.md", "date": date(2025, 11, 25)},
        ]
        result = execute_query(
            records, "SELECT path FROM files WHERE date >= '2025-11-26'"
        )

        assert result["row_count"] == 2
        paths = [r["path"] for r in result["results"]]
        assert "a.md" in paths
        assert "b.md" in paths
        assert "c.md" not in paths

    def test_order_by(self) -> None:
        """Order results."""
        records = [
            {"path": "b.md", "date": date(2025, 11, 26)},
            {"path": "a.md", "date": date(2025, 11, 27)},
        ]
        result = execute_query(records, "SELECT path FROM files ORDER BY date DESC")

        assert result["results"][0]["path"] == "a.md"
        assert result["results"][1]["path"] == "b.md"

    def test_array_contains(self) -> None:
        """Filter by array containment using from_json."""
        records = [
            {"path": "a.md", "tags": ["mcp", "python"]},
            {"path": "b.md", "tags": ["duckdb"]},
            {"path": "c.md", "tags": ["mcp", "duckdb"]},
        ]
        # Arrays are JSON-encoded strings, use from_json to parse
        result = execute_query(
            records,
            """SELECT path FROM files
               WHERE list_contains(from_json(tags, '["VARCHAR"]'), 'mcp')""",
        )

        assert result["row_count"] == 2
        paths = [r["path"] for r in result["results"]]
        assert "a.md" in paths
        assert "c.md" in paths

    def test_aggregate_count(self) -> None:
        """Count records."""
        records = [
            {"path": "a.md"},
            {"path": "b.md"},
            {"path": "c.md"},
        ]
        result = execute_query(records, "SELECT COUNT(*) as count FROM files")

        assert result["row_count"] == 1
        assert result["results"][0]["count"] == 3

    def test_unnest_tags(self) -> None:
        """Unnest array and aggregate using from_json."""
        records = [
            {"path": "a.md", "tags": ["mcp", "python"]},
            {"path": "b.md", "tags": ["mcp"]},
        ]
        # Arrays are JSON-encoded strings, use from_json then unnest
        result = execute_query(
            records,
            """
            SELECT tag, COUNT(*) AS count
            FROM files, UNNEST(from_json(tags, '["VARCHAR"]')) AS t(tag)
            GROUP BY tag
            ORDER BY count DESC
            """,
        )

        assert result["row_count"] == 2
        assert result["results"][0]["tag"] == "mcp"
        assert result["results"][0]["count"] == 2

    def test_empty_records(self) -> None:
        """Handle empty records list."""
        result = execute_query([], "SELECT * FROM files")

        assert result["row_count"] == 0
        assert result["results"] == []

    def test_null_handling(self) -> None:
        """Handle NULL values in records."""
        records = [
            {"path": "a.md", "summary": "Has summary"},
            {"path": "b.md", "summary": None},
            {"path": "c.md"},  # No summary key at all
        ]
        result = execute_query(records, "SELECT path FROM files WHERE summary IS NULL")

        paths = [r["path"] for r in result["results"]]
        assert "b.md" in paths
        assert "c.md" in paths
        assert "a.md" not in paths
