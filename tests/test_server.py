"""Tests for MCP server module."""


class TestServerSetup:
    """Basic tests for server module."""

    def test_import_server(self) -> None:
        """Server module can be imported."""
        from filesystem_frontmatter_mcp import server

        assert hasattr(server, "main")
