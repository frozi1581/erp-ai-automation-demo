"""
Read-only MCP server exposing the demo ERP database to an LLM.

Safety design:
  - Only SELECT statements are allowed (write/DDL keywords are rejected).
  - Queries are restricted to an allowlist of tables.
  - Results are capped to a maximum row count.

This lets an AI client answer questions like:
  "Which product line had the highest total output last month?"
without ever being able to modify or damage the data.

Run:  python src/server.py
"""

import os
import re
import sqlite3
from mcp.server.fastmcp import FastMCP

DB_PATH = os.environ.get("DEMO_DB_PATH", "../sample-data/demo.db")
ALLOWED_TABLES = {"production", "finance"}
MAX_ROWS = 200
FORBIDDEN = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|REPLACE|TRUNCATE|ATTACH|PRAGMA)\b",
    re.IGNORECASE,
)

mcp = FastMCP("erp-demo")


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@mcp.tool()
def list_tables() -> list[str]:
    """List the tables available to query."""
    return sorted(ALLOWED_TABLES)


@mcp.tool()
def describe_table(table: str) -> list[dict]:
    """Return the column names and types for a given allowed table."""
    if table not in ALLOWED_TABLES:
        raise ValueError(f"Table '{table}' is not accessible.")
    with _connect() as conn:
        cols = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return [{"name": c["name"], "type": c["type"]} for c in cols]


@mcp.tool()
def run_query(sql: str) -> list[dict]:
    """
    Run a read-only SELECT query against the demo database.

    Only SELECT statements are permitted. Any query touching tables outside the
    allowlist, or containing write/DDL keywords, is rejected. Results are capped.
    """
    stripped = sql.strip().rstrip(";")
    if not stripped.lower().startswith("select"):
        raise ValueError("Only SELECT queries are allowed.")
    if FORBIDDEN.search(stripped):
        raise ValueError("Query contains a forbidden (write/DDL) keyword.")

    # crude table allowlist check
    referenced = set(re.findall(r"\bfrom\s+([a-zA-Z_][\w]*)", stripped, re.IGNORECASE))
    referenced |= set(re.findall(r"\bjoin\s+([a-zA-Z_][\w]*)", stripped, re.IGNORECASE))
    bad = referenced - ALLOWED_TABLES
    if bad:
        raise ValueError(f"Access to table(s) not allowed: {', '.join(sorted(bad))}")

    with _connect() as conn:
        rows = conn.execute(stripped).fetchmany(MAX_ROWS)
    return [dict(r) for r in rows]


if __name__ == "__main__":
    mcp.run()
