"""Tests for frontmatter parser module."""

from datetime import date
from pathlib import Path

from filesystem_frontmatter_mcp.parser import (
    infer_schema,
    infer_type,
    parse_file,
    parse_files,
)


class TestParseFile:
    """Tests for parse_file function."""

    def test_parse_file_with_frontmatter(self, tmp_path: Path) -> None:
        """Parse a file with valid frontmatter."""
        md_file = tmp_path / "test.md"
        md_file.write_text("""---
date: 2025-11-27
tags: [mcp, python]
summary: Test summary
---
# Content
""")
        result = parse_file(md_file, tmp_path)

        assert result["path"] == "test.md"
        assert result["date"] == date(2025, 11, 27)
        assert result["tags"] == ["mcp", "python"]
        assert result["summary"] == "Test summary"

    def test_parse_file_without_frontmatter(self, tmp_path: Path) -> None:
        """Parse a file without frontmatter returns only path."""
        md_file = tmp_path / "no_frontmatter.md"
        md_file.write_text("# Just content\n\nNo frontmatter here.")

        result = parse_file(md_file, tmp_path)

        assert result["path"] == "no_frontmatter.md"
        assert len(result) == 1

    def test_parse_file_nested_path(self, tmp_path: Path) -> None:
        """Parse a file in a nested directory returns relative path."""
        nested_dir = tmp_path / "atoms" / "sub"
        nested_dir.mkdir(parents=True)
        md_file = nested_dir / "nested.md"
        md_file.write_text("""---
title: Nested
---
""")
        result = parse_file(md_file, tmp_path)

        assert result["path"] == "atoms/sub/nested.md"


class TestParseFiles:
    """Tests for parse_files function."""

    def test_parse_multiple_files(self, tmp_path: Path) -> None:
        """Parse multiple files successfully."""
        file1 = tmp_path / "a.md"
        file1.write_text("""---
date: 2025-11-27
---
""")
        file2 = tmp_path / "b.md"
        file2.write_text("""---
date: 2025-11-26
---
""")
        records, warnings = parse_files([file1, file2], tmp_path)

        assert len(records) == 2
        assert len(warnings) == 0
        assert records[0]["path"] == "a.md"
        assert records[1]["path"] == "b.md"

    def test_parse_files_with_invalid_yaml(self, tmp_path: Path) -> None:
        """Skip files with invalid YAML and report warnings."""
        valid_file = tmp_path / "valid.md"
        valid_file.write_text("""---
title: Valid
---
""")
        invalid_file = tmp_path / "invalid.md"
        invalid_file.write_text("""---
invalid: yaml: content: [
---
""")
        records, warnings = parse_files([valid_file, invalid_file], tmp_path)

        assert len(records) == 1
        assert records[0]["path"] == "valid.md"
        assert len(warnings) == 1
        assert warnings[0]["path"] == "invalid.md"
        assert "error" in warnings[0]


class TestInferType:
    """Tests for infer_type function."""

    def test_string(self) -> None:
        assert infer_type("hello") == "string"

    def test_integer(self) -> None:
        assert infer_type(42) == "integer"

    def test_float(self) -> None:
        assert infer_type(3.14) == "double"

    def test_boolean(self) -> None:
        assert infer_type(True) == "boolean"
        assert infer_type(False) == "boolean"

    def test_date(self) -> None:
        assert infer_type(date(2025, 11, 27)) == "date"

    def test_list_of_strings(self) -> None:
        assert infer_type(["a", "b", "c"]) == "array<string>"

    def test_empty_list(self) -> None:
        assert infer_type([]) == "array"

    def test_mixed_list(self) -> None:
        assert infer_type([1, "two", 3]) == "array"

    def test_null(self) -> None:
        assert infer_type(None) == "null"

    def test_dict(self) -> None:
        assert infer_type({"key": "value"}) == "json"


class TestInferSchema:
    """Tests for infer_schema function."""

    def test_basic_types(self) -> None:
        """Infer schema with date and array<string> types."""
        records = [
            {"path": "a.md", "date": date(2025, 11, 27), "tags": ["mcp"]},
            {"path": "b.md", "date": date(2025, 11, 26), "tags": ["python", "duckdb"]},
        ]
        schema = infer_schema(records)

        assert schema["date"]["type"] == "date"
        assert schema["date"]["count"] == 2
        assert schema["date"]["nullable"] is False

        assert schema["tags"]["type"] == "array<string>"
        assert schema["tags"]["count"] == 2

    def test_nullable_detection(self) -> None:
        """Detect nullable fields when some records lack the property."""
        records = [
            {"path": "a.md", "title": "Title A", "summary": "Summary"},
            {"path": "b.md", "title": "Title B"},
        ]
        schema = infer_schema(records)

        assert schema["title"]["nullable"] is False
        assert schema["summary"]["nullable"] is True
        assert schema["summary"]["count"] == 1

    def test_sample_values_unique(self) -> None:
        """Sample values are unique and limited by max_samples."""
        records = [
            {"path": "a.md", "category": "tech"},
            {"path": "b.md", "category": "life"},
            {"path": "c.md", "category": "tech"},
        ]
        schema = infer_schema(records, max_samples=2)

        assert len(schema["category"]["sample_values"]) == 2
        assert "tech" in schema["category"]["sample_values"]
        assert "life" in schema["category"]["sample_values"]

    def test_excludes_path(self) -> None:
        """Path property should not appear in schema."""
        records = [{"path": "a.md", "title": "A"}]
        schema = infer_schema(records)

        assert "path" not in schema
        assert "title" in schema
