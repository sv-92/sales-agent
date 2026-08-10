"""Database seeding for the demo CRM."""

import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
DB_PATH = DATA_DIR / "crm.db"
SEED_SQL = DATA_DIR / "seed_data.sql"


def ensure_seeded():
    """Create and seed the database if it doesn't exist or is empty."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(DB_PATH))
    try:
        # Check if deals table exists and has data
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='deals'"
        )
        if cursor.fetchone():
            count = conn.execute("SELECT COUNT(*) FROM deals").fetchone()[0]
            if count > 0:
                logger.info(f"Database already seeded ({count} deals)")
                return

        # Run seed script
        if SEED_SQL.exists():
            sql = SEED_SQL.read_text(encoding="utf-8")
            conn.executescript(sql)
            logger.info("Database seeded from seed_data.sql")
        else:
            logger.warning(f"Seed file not found: {SEED_SQL}")
    finally:
        conn.close()
