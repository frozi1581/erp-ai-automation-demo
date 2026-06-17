# n8n Workflow — Scheduled ERP Extract

Imports source data on a schedule, transforms it, and upserts into the database —
the "extract & land" half of the pipeline.

## Import
n8n → **Workflows** → **Import from File** → select `erp-extract-workflow.json`.

## What it does
1. **Schedule Trigger** — runs daily (cron configurable)
2. **Read Source** — reads the source CSV/API (demo uses an HTTP node)
3. **Transform** — normalizes fields, computes derived columns
4. **Upsert to DB** — writes into the `production` table (insert-or-update)

## Notes
This is a sanitized skeleton. In a real deployment the source node points at the
ERP export / API and the DB node at MySQL. Credentials live in n8n's credential
vault, never in the workflow JSON.
