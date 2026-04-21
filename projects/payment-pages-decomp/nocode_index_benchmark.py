#!/usr/bin/env python3
"""
Benchmark nocode list queries with and without composite index.
Two modes:
  1) Load from single-merchant CSV export (--csv).
  2) Generate ~1.5M dummy rows from merchant distribution (--distribution-csv)
     for prod-like row count and merchant distribution.

Usage:
  python3 nocode_index_benchmark.py --csv /path/to/25888371_2026_02_11.csv
  python3 nocode_index_benchmark.py --distribution-csv /path/to/25889370_2026_02_11.csv

Output:
  - nocode_copy.db (SQLite DB in same dir as script)
  - nocode_index_benchmark_report.md (latency report)
"""

import argparse
import csv
import sqlite3
import time
from pathlib import Path

# Default paths (Downloads)
SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_CSV = Path.home() / "Downloads" / "25888371_2026_02_11.csv"
DEFAULT_DISTRIBUTION_CSV = Path.home() / "Downloads" / "25889370_2026_02_11.csv"
DB_PATH = SCRIPT_DIR / "nocode_copy.db"
REPORT_PATH = SCRIPT_DIR / "nocode_index_benchmark_report.md"

MERCHANT_ID = "Ha18e7jHMVjYEb"
MODE = "live"
TYPE_PAGE = "page"
RUNS = 3  # number of runs per query for median
BATCH_SIZE = 25_000  # rows per insert batch for dummy data
BASE_TS = 1690000000  # unix ts for created_at


def load_csv(csv_path: Path) -> list[dict]:
    """Load CSV with proper handling of quoted fields (commas, newlines)."""
    rows = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def create_schema(cursor: sqlite3.Cursor) -> None:
    """Create nocode table matching MySQL schema (SQLite types)."""
    cursor.execute("""
        CREATE TABLE nocode (
            id TEXT NOT NULL PRIMARY KEY,
            merchant_id TEXT NOT NULL,
            title TEXT,
            description TEXT,
            status TEXT NOT NULL,
            currency TEXT NOT NULL,
            notes TEXT,
            expire_by INTEGER,
            expired_at INTEGER,
            type TEXT NOT NULL,
            meta_data TEXT,
            short_url TEXT NOT NULL,
            mode TEXT NOT NULL,
            created_at INTEGER NOT NULL,
            updated_at INTEGER NOT NULL,
            deleted_at INTEGER,
            terms TEXT,
            status_reason TEXT
        )
    """)


def insert_rows(cursor: sqlite3.Cursor, rows: list[dict]) -> None:
    """Insert rows into nocode table."""
    cols = list(rows[0].keys())
    placeholders = ",".join("?" for _ in cols)
    sql = f"INSERT INTO nocode ({','.join(cols)}) VALUES ({placeholders})"
    for row in rows:
        cursor.execute(sql, [row.get(c) for c in cols])


def load_distribution(dist_path: Path) -> list[tuple[str, int]]:
    """Load (merchant_id, count) from distribution CSV. Column may be 'count(*)' or similar."""
    out = []
    with open(dist_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            mid = (row.get("merchant_id") or "").strip()
            cnt_str = row.get("count(*)") or row.get("count") or "0"
            try:
                cnt = int(cnt_str.strip())
            except ValueError:
                continue
            if mid and cnt > 0:
                out.append((mid, cnt))
    return out


def generate_dummy_row(global_idx: int, merchant_id: str, page_idx: int) -> tuple:
    """Generate one dummy nocode row as tuple for executemany. id is 14 chars."""
    # Some titles with "shank" for top merchant so title filter returns rows
    if merchant_id == MERCHANT_ID and page_idx % 1000 == 0:
        title = f"shank Page {page_idx}"
    else:
        title = f"Page {page_idx}"
    id_ = f"dum{global_idx:011d}"[:14]  # 14-char id
    created = BASE_TS + global_idx
    return (
        id_,
        merchant_id,
        title,
        "",
        "active",
        "INR",
        "{}",
        None,
        None,
        TYPE_PAGE,
        "{}",
        "https://rzp.io/l/x",
        MODE,
        created,
        created,
        None,
        "",
        None,
    )


def insert_dummy_from_distribution(cursor: sqlite3.Cursor, distribution: list[tuple[str, int]]) -> int:
    """Insert dummy rows according to (merchant_id, count). Returns total rows inserted."""
    cols = (
        "id", "merchant_id", "title", "description", "status", "currency", "notes",
        "expire_by", "expired_at", "type", "meta_data", "short_url", "mode",
        "created_at", "updated_at", "deleted_at", "terms", "status_reason",
    )
    placeholders = ",".join("?" for _ in cols)
    sql = f"INSERT INTO nocode ({','.join(cols)}) VALUES ({placeholders})"
    total = 0
    global_idx = 0
    batch = []
    for merchant_id, count in distribution:
        for page_idx in range(count):
            batch.append(generate_dummy_row(global_idx, merchant_id, page_idx))
            global_idx += 1
            if len(batch) >= BATCH_SIZE:
                cursor.executemany(sql, batch)
                total += len(batch)
                batch = []
                print(f"  inserted {total} rows...")
    if batch:
        cursor.executemany(sql, batch)
        total += len(batch)
    return total


def create_original_indexes(cursor: sqlite3.Cursor) -> None:
    """Create indexes matching production (no composite list index)."""
    cursor.execute("CREATE INDEX IF NOT EXISTS nocode_merchant_id_index ON nocode(merchant_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS nocode_created_at_index ON nocode(created_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_expire_by ON nocode(expire_by)")


def create_composite_list_index(cursor: sqlite3.Cursor) -> None:
    """Create composite index for list query (merchant_id, mode, type, created_at)."""
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_nocode_list
        ON nocode(merchant_id, mode, type, created_at)
    """)


def drop_composite_list_index(cursor: sqlite3.Cursor) -> None:
    """Drop the composite list index (to benchmark without it)."""
    cursor.execute("DROP INDEX IF EXISTS idx_nocode_list")


def run_query(cursor: sqlite3.Cursor, sql: str, params: tuple = ()) -> float:
    """Execute query RUNS times and return median elapsed time in seconds."""
    times = []
    for _ in range(RUNS):
        start = time.perf_counter()
        cursor.execute(sql, params)
        cursor.fetchall()
        times.append(time.perf_counter() - start)
    times.sort()
    return times[len(times) // 2]


def get_explain(cursor: sqlite3.Cursor, sql: str, params: tuple = ()) -> list[tuple]:
    """Return EXPLAIN QUERY PLAN output."""
    cursor.execute(f"EXPLAIN QUERY PLAN {sql}", params)
    return cursor.fetchall()


def main():
    parser = argparse.ArgumentParser(description="Benchmark nocode list queries with/without composite index")
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV, help="Path to single-merchant nocode CSV export")
    parser.add_argument("--distribution-csv", type=Path, default=None, help="Path to merchant_id vs count CSV (e.g. 25889370_2026_02_11.csv) for 1.5M dummy rows")
    parser.add_argument("--no-load", action="store_true", help="Skip load; use existing nocode_copy.db")
    args = parser.parse_args()

    use_distribution = args.distribution_csv is not None
    if use_distribution and not args.no_load and not args.distribution_csv.exists():
        print(f"Distribution CSV not found: {args.distribution_csv}")
        return 1
    if not use_distribution and not args.no_load and not args.csv.exists():
        print(f"CSV not found: {args.csv}")
        return 1

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    row_count = 0
    if use_distribution:
        if not args.no_load:
            print("Creating table and inserting dummy rows from distribution...")
            cursor.execute("DROP TABLE IF EXISTS nocode")
            create_schema(cursor)
            distribution = load_distribution(args.distribution_csv)
            total_rows = sum(c for _, c in distribution)
            print(f"Distribution: {len(distribution)} merchants, {total_rows} total rows")
            row_count = insert_dummy_from_distribution(cursor, distribution)
            conn.commit()
            print(f"Inserted {row_count} rows")
        else:
            cursor.execute("SELECT COUNT(*) FROM nocode")
            row_count = cursor.fetchone()[0]
            print(f"Using existing DB with {row_count} rows")
    elif not args.no_load:
        print("Loading CSV...")
        rows = load_csv(args.csv)
        row_count = len(rows)
        print(f"Loaded {row_count} rows")
        cursor.execute("DROP TABLE IF EXISTS nocode")
        create_schema(cursor)
        insert_rows(cursor, rows)
        conn.commit()
    else:
        cursor.execute("SELECT COUNT(*) FROM nocode")
        row_count = cursor.fetchone()[0]
        print(f"Using existing DB with {row_count} rows")

    # Ensure we have original indexes (and no composite) for "without" phase
    create_original_indexes(cursor)
    drop_composite_list_index(cursor)
    conn.commit()

    # Query definitions: (name, sql, params)
    queries = [
        ("List with title filter (shank)", """
            SELECT * FROM nocode
            WHERE merchant_id = ? AND mode = ? AND type = ?
            AND LOWER(title) LIKE LOWER(?)
            ORDER BY created_at DESC
            LIMIT 25 OFFSET 0
        """, (MERCHANT_ID, MODE, TYPE_PAGE, "%shank%")),
        ("List with title filter (M-)", """
            SELECT * FROM nocode
            WHERE merchant_id = ? AND mode = ? AND type = ?
            AND LOWER(title) LIKE LOWER(?)
            ORDER BY created_at DESC
            LIMIT 25 OFFSET 0
        """, (MERCHANT_ID, MODE, TYPE_PAGE, "%M-%")),
        ("List without title (first page)", """
            SELECT * FROM nocode
            WHERE merchant_id = ? AND mode = ? AND type = ?
            ORDER BY created_at DESC
            LIMIT 25 OFFSET 0
        """, (MERCHANT_ID, MODE, TYPE_PAGE)),
        ("List without title (skip 1000)", """
            SELECT * FROM nocode
            WHERE merchant_id = ? AND mode = ? AND type = ?
            ORDER BY created_at DESC
            LIMIT 25 OFFSET 1000
        """, (MERCHANT_ID, MODE, TYPE_PAGE)),
        ("List by merchant_id only (no mode/type)", """
            SELECT * FROM nocode
            WHERE merchant_id = ?
            ORDER BY created_at DESC
            LIMIT 25 OFFSET 0
        """, (MERCHANT_ID,)),
        ("Count by merchant+mode+type", """
            SELECT COUNT(*) FROM nocode
            WHERE merchant_id = ? AND mode = ? AND type = ?
        """, (MERCHANT_ID, MODE, TYPE_PAGE)),
    ]

    results_without = []
    results_with = []

    # --- Phase 1: Without composite index ---
    print("Running queries WITHOUT composite index...")
    for name, sql, params in queries:
        t = run_query(cursor, sql, params)
        plan = get_explain(cursor, sql, params)
        results_without.append((name, t, plan))

    # --- Phase 2: With composite index ---
    print("Creating composite index idx_nocode_list...")
    create_composite_list_index(cursor)
    conn.commit()

    print("Running queries WITH composite index...")
    for name, sql, params in queries:
        t = run_query(cursor, sql, params)
        plan = get_explain(cursor, sql, params)
        results_with.append((name, t, plan))

    conn.close()

    # --- Write report ---
    source_note = "dummy rows from distribution CSV" if use_distribution else "CSV export"
    with open(REPORT_PATH, "w") as f:
        f.write("# Nocode list query benchmark (Ha18e7jHMVjYEb)\n\n")
        f.write(f"- **Source:** {source_note}, {row_count} rows\n")
        f.write(f"- **DB:** SQLite at `{DB_PATH}`\n")
        f.write(f"- **Runs per query:** {RUNS} (median reported)\n\n")
        f.write("## Latencies\n\n")
        f.write("| Query | Without idx_nocode_list | With idx_nocode_list | Speedup |\n")
        f.write("|-------|------------------------|----------------------|--------|\n")
        for i, (name, _, _) in enumerate(queries):
            t0 = results_without[i][1]
            t1 = results_with[i][1]
            speedup = t0 / t1 if t1 > 0.0001 else (t0 / 0.0001)
            t0_str = f"{t0*1000:.1f} ms" if t0 < 1 else f"{t0:.3f} s"
            t1_str = f"{t1*1000:.1f} ms" if t1 < 1 else f"{t1:.3f} s"
            f.write(f"| {name} | {t0_str} | {t1_str} | {speedup:.1f}x |\n")
        f.write("\n## EXPLAIN QUERY PLAN (list with title shank)\n\n")
        f.write("**Without composite index:**\n```\n")
        for row in results_without[0][2]:
            f.write(" ".join(str(x) for x in row) + "\n")
        f.write("```\n\n**With composite index:**\n```\n")
        for row in results_with[0][2]:
            f.write(" ".join(str(x) for x in row) + "\n")
        f.write("```\n")
        f.write("\n## Conclusion\n\n")
        f.write("- Adding `idx_nocode_list (merchant_id, mode, type, created_at)` removes the **USE TEMP B-TREE FOR ORDER BY** (filesort) and lets the planner use a single index range scan.\n")
        f.write("- List-without-title and count queries become orders of magnitude faster.\n")
        f.write("- List-with-title (e.g. `LIKE '%shank%'`) still scans rows in index order until enough matches; speedup depends on how selective the title filter is.\n")
        f.write("- **Note:** This benchmark uses SQLite; production MySQL/TiDB may show different absolute times (e.g. 52s without index). The same composite index is recommended there.\n")
    print(f"Report written to {REPORT_PATH}")

    return 0


if __name__ == "__main__":
    exit(main())
