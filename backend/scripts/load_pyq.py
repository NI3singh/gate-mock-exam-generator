"""
CLI: load PYQ JSON files (data/pyq/json/*.json) into the database with embeddings.

Run from the backend/ directory:

    python scripts/load_pyq.py

Idempotent per (paper, year) — safe to re-run after editing/adding JSON files.
Requires the database to be reachable and `sentence-transformers` installed for
embeddings (without it, rows load but retrieval will be inactive).
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import AsyncSessionLocal
from app.services.pyq_loader import load_pyq_files


async def main() -> None:
    async with AsyncSessionLocal() as db:
        result = await load_pyq_files(db)

    print("PYQ load result")
    print(f"  embeddings available: {result['embeddings_available']}")
    for f in result["files"]:
        print(
            f"  {f['file']}: {f['questions']} questions "
            f"(paper={f['paper']}, year={f['year']}, embedded={f['embedded']})"
        )
    print(f"  total questions loaded: {result['total_questions']}")
    if result["errors"]:
        print("  errors:")
        for err in result["errors"]:
            print(f"    - {err}")


if __name__ == "__main__":
    asyncio.run(main())
