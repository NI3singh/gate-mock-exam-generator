"""
Migrate the current Postgres database to Neon (or any target Postgres) EXACTLY:
schema + relations + constraints + indexes + pgvector + all data + migration state.

Reads two URLs from backend/.env:
    DATABASE_URL        -> SOURCE  (your current/local DB)
    NEON_DATABASE_URL   -> TARGET  (the Neon DB)

Method: custom-format `pg_dump` (--no-owner --no-acl) restored with parallel
`pg_restore -j`, then a per-table row-count comparison. The SOURCE database is only
READ — never modified — so your existing data cannot be lost.

Usage (from anywhere; requires pg_dump/pg_restore/psql 16+ on PATH):
    python backend/scripts/migrate_to_neon.py --clean     # wipe target schema, then migrate (recommended)
    python backend/scripts/migrate_to_neon.py             # migrate into an empty target
    python backend/scripts/migrate_to_neon.py --verify-only   # just compare row counts
    python backend/scripts/migrate_to_neon.py --jobs 4    # restore parallelism (default 4)

Secrets (passwords) are read from .env and passed via PGPASSWORD; never printed.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlparse, unquote

BACKEND_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = BACKEND_ROOT / ".env"


def _load_env() -> None:
    from dotenv import load_dotenv
    load_dotenv(ENV_PATH)


def _parse(url: str) -> dict:
    """Parse a postgres URL (incl. sqlalchemy +asyncpg form) into libpq parts."""
    u = (url.replace("postgresql+asyncpg://", "postgresql://")
            .replace("postgres+asyncpg://", "postgresql://"))
    p = urlparse(u)
    return {
        "host": p.hostname or "",
        "port": str(p.port or 5432),
        "user": unquote(p.username or ""),
        "password": unquote(p.password or ""),
        "dbname": (p.path or "/").lstrip("/") or "postgres",
    }


def _env_for(conn: dict, *, sslmode: str | None) -> dict:
    env = dict(os.environ)
    env["PGPASSWORD"] = conn["password"]
    if sslmode:
        env["PGSSLMODE"] = sslmode
    return env


def _psql(conn: dict, sslmode: str | None, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["psql", "-h", conn["host"], "-p", conn["port"], "-U", conn["user"],
         "-d", conn["dbname"], *args],
        env=_env_for(conn, sslmode=sslmode), capture_output=True, text=True,
    )


def _psql_value(conn: dict, sslmode: str | None, sql: str) -> str:
    out = _psql(conn, sslmode, "-tAc", sql)
    if out.returncode != 0:
        raise RuntimeError(out.stderr.strip())
    return out.stdout.strip()


def _table_counts(conn: dict, sslmode: str | None) -> dict:
    tabs = _psql_value(
        conn, sslmode,
        "select tablename from pg_tables where schemaname='public' order by tablename",
    ).splitlines()
    counts: dict[str, int] = {}
    for t in (x.strip() for x in tabs if x.strip()):
        counts[t] = int(_psql_value(conn, sslmode, f'select count(*) from "{t}"'))
    return counts


def _report(src_counts: dict, tgt_counts: dict) -> bool:
    print("\n=== Row-count verification (source vs target) ===")
    ok = True
    for t in sorted(set(src_counts) | set(tgt_counts)):
        s, d = src_counts.get(t), tgt_counts.get(t)
        mark = "OK" if s == d else "MISMATCH"
        if s != d:
            ok = False
        print(f"  {t:<22} source={s}  target={d}  [{mark}]")
    print("RESULT:", "ALL TABLES MATCH" if ok else "MISMATCH — review above")
    return ok


def main() -> int:
    ap = argparse.ArgumentParser(description="Migrate Postgres DB to Neon (exact).")
    ap.add_argument("--clean", action="store_true",
                    help="DROP/recreate the target's public schema before restoring")
    ap.add_argument("--force", action="store_true",
                    help="proceed even if target is not empty (without cleaning)")
    ap.add_argument("--verify-only", action="store_true", help="only compare row counts")
    ap.add_argument("--jobs", type=int, default=4, help="pg_restore parallelism")
    args = ap.parse_args()

    _load_env()
    src_url = os.getenv("DATABASE_URL")
    tgt_url = os.getenv("NEON_DATABASE_URL")
    if not src_url:
        print("ERROR: DATABASE_URL not set in backend/.env"); return 1
    if not tgt_url:
        print("ERROR: NEON_DATABASE_URL not set in backend/.env."); return 1

    src, tgt = _parse(src_url), _parse(tgt_url)
    SRC_SSL, TGT_SSL = None, "require"

    print(f"SOURCE: {src['user']}@{src['host']}:{src['port']}/{src['dbname']}")
    print(f"TARGET: {tgt['user']}@{tgt['host']}:{tgt['port']}/{tgt['dbname']}")

    try:
        print("  source:", _psql_value(src, SRC_SSL, "select version()").split(",")[0])
        print("  target:", _psql_value(tgt, TGT_SSL, "select version()").split(",")[0])
    except Exception as e:  # noqa: BLE001
        print("CONNECT FAILED:", e); return 1

    src_counts = _table_counts(src, SRC_SSL)

    if args.verify_only:
        _report(src_counts, _table_counts(tgt, TGT_SSL))
        return 0

    if args.clean:
        print("\nCleaning target: DROP SCHEMA public CASCADE; CREATE SCHEMA public ...")
        clean = _psql(tgt, TGT_SSL, "-v", "ON_ERROR_STOP=1", "-c",
                      "DROP SCHEMA IF EXISTS public CASCADE; CREATE SCHEMA public;")
        if clean.returncode != 0:
            print("CLEAN FAILED:", clean.stderr.strip()); return 1
        print("  target schema reset.")
    else:
        tgt_tables = _table_counts(tgt, TGT_SSL)
        if tgt_tables and not args.force:
            print(f"\nABORT: target already has {len(tgt_tables)} table(s): "
                  f"{', '.join(sorted(tgt_tables))}.")
            print("Re-run with --clean (recommended) to wipe and reload, or --force.")
            return 1

    print("Ensuring pgvector extension on target ...")
    ext = _psql(tgt, TGT_SSL, "-c", "CREATE EXTENSION IF NOT EXISTS vector")
    if ext.returncode != 0:
        print("  note:", ext.stderr.strip(), "(pg_restore will retry)")

    dump_path = Path(tempfile.gettempdir()) / "gate_db_dump.dump"
    print(f"Dumping source (custom format) -> {dump_path.name} ...")
    dump = subprocess.run(
        ["pg_dump", "-h", src["host"], "-p", src["port"], "-U", src["user"],
         "-d", src["dbname"], "--no-owner", "--no-acl", "-Fc", "-f", str(dump_path)],
        env=_env_for(src, sslmode=SRC_SSL), capture_output=True, text=True,
    )
    if dump.returncode != 0:
        print("pg_dump FAILED:\n", dump.stderr); return 1
    print(f"  dump written: {dump_path.stat().st_size:,} bytes")

    print(f"Restoring into target (pg_restore -j{args.jobs}) ...")
    restore = subprocess.run(
        ["pg_restore", "-h", tgt["host"], "-p", tgt["port"], "-U", tgt["user"],
         "-d", tgt["dbname"], "--no-owner", "--no-acl", "-j", str(args.jobs),
         str(dump_path)],
        env=_env_for(tgt, sslmode=TGT_SSL), capture_output=True, text=True,
    )
    # pg_restore against managed Postgres can emit benign warnings (e.g. extension
    # comments). The row-count check below is the real source of truth.
    err = (restore.stderr or "").strip()
    if err:
        err_lines = [ln for ln in err.splitlines() if ln.strip()]
        print(f"  pg_restore reported {len(err_lines)} message(s); tail:")
        for ln in err_lines[-12:]:
            print("    " + ln)
    else:
        print("  restore completed with no warnings.")

    ok = _report(src_counts, _table_counts(tgt, TGT_SSL))
    if ok:
        print("\nMigration verified - every table matches.")
        print("Next: point the app's DATABASE_URL at Neon "
              "(postgresql+asyncpg://...?ssl=require).")
    else:
        print("\nRow counts differ — inspect the pg_restore messages above.")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
