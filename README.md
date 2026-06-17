# ERP-to-Dashboard AI Automation Demo

A reference implementation showing how to connect an enterprise-style database to
modern AI tooling using **n8n**, the **Model Context Protocol (MCP)**, and a small
**Python** extraction layer.

This is a sanitized, public demo built on **synthetic data** — no real company data,
credentials, or schemas are included. It mirrors a real production pattern: pulling
operational/financial data from a source system on a schedule, landing it in a
database, and exposing it to an LLM so non-technical users can ask plain-language
questions about live data.

---

## What it demonstrates

| Capability | Component |
|---|---|
| Scheduled data extraction & transformation | `n8n/` workflow |
| AI-to-database access (natural language → SQL → answer) | `mcp-server/` |
| Realistic enterprise data shape (production + finance) | `sample-data/` |
| Clean, reproducible setup | this README |

---

## Architecture

```
┌──────────────┐     scheduled      ┌──────────────┐      query      ┌──────────────┐
│  Source data │ ─────extract─────▶ │   Database   │ ◀──────────────│  MCP server  │
│ (CSV / API)  │   (n8n workflow)   │  (SQLite/    │   structured    │  (Python)    │
└──────────────┘                    │   MySQL)     │    SQL access   └──────┬───────┘
                                    └──────────────┘                        │
                                                                   natural language
                                                                            │
                                                                     ┌──────▼───────┐
                                                                     │  LLM client  │
                                                                     │ (Claude etc) │
                                                                     └──────────────┘
```

A manager asks *"Which product line had the highest output last month?"* — the LLM
calls the MCP server, which safely runs a read-only query against the database and
returns the answer in plain language.

---

## Quick start

### 1. Generate the sample database
```bash
cd sample-data
python generate_data.py        # creates demo.db with synthetic production + finance data
```

### 2. Run the MCP server
```bash
cd mcp-server
pip install -r requirements.txt
python src/server.py
```
Then connect it to any MCP-compatible client (e.g. Claude Desktop) using the config
in `mcp-server/README.md`.

### 3. Import the n8n workflow
Import `n8n/erp-extract-workflow.json` into your n8n instance. It runs on a schedule,
reads source data, transforms it, and upserts into the database. See `n8n/README.md`.

---

## Tech stack

- **n8n** — workflow orchestration / scheduling
- **Python** — extraction + MCP server (FastMCP)
- **SQLite** (demo) / **MySQL** (production-equivalent)
- **MCP** — safe, read-only AI access to the data layer

---

## Why this pattern matters

Most automation work lives at one of two extremes: pure AI demos with no real data,
or rigid enterprise integrations with no intelligence. This demo sits at the
intersection — **real enterprise data shapes** made queryable by an LLM through a
controlled, auditable interface. That's the combination that turns fragile manual
reporting into a reliable, self-service system.

---

## Notes on safety

- All data is **synthetic**, generated locally.
- The MCP server is **read-only** and **allowlists** which tables/columns can be queried.
- No credentials are committed; configuration is via environment variables.

## License

MIT
