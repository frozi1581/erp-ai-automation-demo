# MCP Server — ERP Demo

A read-only MCP server that lets an LLM client query the synthetic ERP database
in plain language.

## Tools exposed
- `list_tables()` — list queryable tables
- `describe_table(table)` — column names & types
- `run_query(sql)` — run a **read-only SELECT** (write/DDL keywords rejected, tables allowlisted, results capped)

## Run
```bash
pip install -r requirements.txt
python src/server.py
```

## Connect to Claude Desktop
Add to your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "erp-demo": {
      "command": "python",
      "args": ["/absolute/path/to/mcp-server/src/server.py"],
      "env": { "DEMO_DB_PATH": "/absolute/path/to/sample-data/demo.db" }
    }
  }
}
```

## Example questions it can answer
- "Which product line had the highest total output in the last 30 days?"
- "What was the gross margin per cost center last month?"
- "Show daily defect rate trend for Precast Beam."

## Safety
Only `SELECT` is permitted. Queries are checked against a forbidden-keyword list and
a table allowlist, and results are capped at 200 rows.
