"""
Generate a synthetic ERP-style SQLite database for the demo.

Creates two tables that mimic the shape of real enterprise data without
containing any real records:
  - production : daily output per product line
  - finance    : monthly revenue / cost per cost center

Run:  python generate_data.py
Output: demo.db
"""

import sqlite3
import random
from datetime import date, timedelta

random.seed(42)  # reproducible

PRODUCT_LINES = ["Precast Beam", "Concrete Pile", "Box Girder", "Wall Panel", "Sleeper"]
COST_CENTERS = ["Plant-A", "Plant-B", "Plant-C", "Logistics", "Maintenance"]

DB_PATH = "demo.db"


def build_schema(cur):
    cur.executescript(
        """
        DROP TABLE IF EXISTS production;
        DROP TABLE IF EXISTS finance;

        CREATE TABLE production (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            prod_date     TEXT    NOT NULL,
            product_line  TEXT    NOT NULL,
            output_units  INTEGER NOT NULL,
            defect_units  INTEGER NOT NULL
        );

        CREATE TABLE finance (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            period        TEXT    NOT NULL,   -- YYYY-MM
            cost_center   TEXT    NOT NULL,
            revenue       REAL    NOT NULL,
            cost          REAL    NOT NULL
        );
        """
    )


def seed_production(cur):
    start = date.today() - timedelta(days=90)
    rows = []
    for d in range(90):
        day = start + timedelta(days=d)
        if day.weekday() == 6:  # skip Sundays
            continue
        for line in PRODUCT_LINES:
            output = random.randint(40, 160)
            defects = random.randint(0, max(1, output // 25))
            rows.append((day.isoformat(), line, output, defects))
    cur.executemany(
        "INSERT INTO production (prod_date, product_line, output_units, defect_units) "
        "VALUES (?, ?, ?, ?)",
        rows,
    )
    return len(rows)


def seed_finance(cur):
    rows = []
    today = date.today()
    for m in range(6):  # last 6 months
        year = today.year
        month = today.month - m
        while month <= 0:
            month += 12
            year -= 1
        period = f"{year:04d}-{month:02d}"
        for cc in COST_CENTERS:
            revenue = round(random.uniform(80_000, 400_000), 2)
            cost = round(revenue * random.uniform(0.55, 0.85), 2)
            rows.append((period, cc, revenue, cost))
    cur.executemany(
        "INSERT INTO finance (period, cost_center, revenue, cost) VALUES (?, ?, ?, ?)",
        rows,
    )
    return len(rows)


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    build_schema(cur)
    p = seed_production(cur)
    f = seed_finance(cur)
    conn.commit()
    conn.close()
    print(f"Created {DB_PATH}: {p} production rows, {f} finance rows.")


if __name__ == "__main__":
    main()
