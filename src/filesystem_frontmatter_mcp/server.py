"""MCP Server implementation."""

import argparse
import glob as globmodule
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from filesystem_frontmatter_mcp.parser import infer_schema, parse_files
from filesystem_frontmatter_mcp.query import execute_query

# Global base directory
_base_dir: Path | None = None


def get_base_dir() -> Path:
    """Get the configured base directory."""
    if _base_dir is None:
        raise RuntimeError("Base directory not configured. Use --base-dir argument.")
    return _base_dir


def collect_files(glob_pattern: str) -> list[Path]:
    """Collect files matching the glob pattern.

    Args:
        glob_pattern: Glob pattern relative to base directory.

    Returns:
        List of absolute paths to matching files.
    """
    base = get_base_dir()
    pattern = str(base / glob_pattern)
    matches = globmodule.glob(pattern, recursive=True)
    return [Path(p) for p in matches if Path(p).is_file()]


def create_server() -> Server:
    """Create and configure the MCP server."""
    server = Server("filesystem-frontmatter-mcp")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available tools."""
        return [
            Tool(
                name="inspect_frontmatter",
                description="Get frontmatter schema from files matching glob pattern.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "glob": {
                            "type": "string",
                            "description": "Glob pattern relative to base directory.",
                        }
                    },
                    "required": ["glob"],
                },
            ),
            Tool(
                name="query_frontmatter",
                description="Query frontmatter with DuckDB SQL.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "glob": {
                            "type": "string",
                            "description": "Glob pattern relative to base directory.",
                        },
                        "sql": {
                            "type": "string",
                            "description": "SQL query. Reference 'files' table.",
                        },
                    },
                    "required": ["glob", "sql"],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle tool calls."""
        import json

        base = get_base_dir()

        if name == "inspect_frontmatter":
            glob_pattern = arguments["glob"]
            paths = collect_files(glob_pattern)
            records, warnings = parse_files(paths, base)
            schema = infer_schema(records)

            result = {
                "file_count": len(records),
                "schema": schema,
            }
            if warnings:
                result["warnings"] = warnings

            return [TextContent(type="text", text=json.dumps(result, default=str))]

        elif name == "query_frontmatter":
            glob_pattern = arguments["glob"]
            sql = arguments["sql"]
            paths = collect_files(glob_pattern)
            records, warnings = parse_files(paths, base)
            query_result = execute_query(records, sql)

            result: dict[str, Any] = {
                "results": query_result["results"],
                "row_count": query_result["row_count"],
                "columns": query_result["columns"],
            }
            if warnings:
                result["warnings"] = warnings

            return [TextContent(type="text", text=json.dumps(result, default=str))]

        else:
            raise ValueError(f"Unknown tool: {name}")

    return server


async def run_server() -> None:
    """Run the MCP server."""
    server = create_server()
    async with stdio_server() as (read_stream, write_stream):
        init_options = server.create_initialization_options()
        await server.run(read_stream, write_stream, init_options)


def main() -> None:
    """Entry point for the MCP server."""
    global _base_dir

    parser = argparse.ArgumentParser(description="Filesystem Frontmatter MCP Server")
    parser.add_argument(
        "--base-dir",
        type=str,
        required=True,
        help="Base directory for glob patterns",
    )
    args = parser.parse_args()

    _base_dir = Path(args.base_dir).resolve()
    if not _base_dir.is_dir():
        parser.error(f"Base directory does not exist: {_base_dir}")

    import asyncio

    asyncio.run(run_server())


if __name__ == "__main__":
    main()
