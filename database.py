# database.py — SQLite Database for Scan History
# LOCATION: app/database.py
import sqlite3
import logging
import json
from pathlib import Path
from contextlib import contextmanager

# =========================
# LOGGING SETUP
# =========================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =========================
# CONSTANTS
# FIX: DB lives at project_root/database/scans.db
#      Path(__file__).parent      → app/
#      Path(__file__).parent.parent → project root
# =========================
DB_DIR = Path(__file__).parent.parent / "database"
DB_PATH = DB_DIR / "scans.db"
DB_DIR.mkdir(parents=True, exist_ok=True)


# =========================
# CONNECTION MANAGER
# =========================
@contextmanager
def get_db_connection():
    """Thread-safe SQLite connection with Row factory."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


# =========================
# INITIALIZATION
# =========================
def create_database():
    """Creates scan_history table if it does not already exist."""
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS scan_history (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp     DATETIME DEFAULT CURRENT_TIMESTAMP,
                url           TEXT     NOT NULL,
                risk_score    INTEGER  NOT NULL,
                risk_category TEXT     NOT NULL,
                reasons       TEXT
            )
        ''')
        conn.commit()
    logger.info("✅ Database initialised / verified.")


# =========================
# INSERT
# =========================
def insert_scan(url: str, risk_score: int, risk_category: str, reasons: list):
    """Inserts a new scan record; reasons serialised as JSON."""
    try:
        reasons_json = json.dumps(reasons)
        with get_db_connection() as conn:
            conn.execute(
                '''INSERT INTO scan_history (url, risk_score, risk_category, reasons)
                   VALUES (?, ?, ?, ?)''',
                (url, risk_score, risk_category, reasons_json)
            )
            conn.commit()
        logger.info(f"✅ Scan inserted: {url}  ({risk_category}, score={risk_score})")
    except sqlite3.Error as e:
        logger.error(f"❌ Insertion failed: {e}")


# =========================
# RETRIEVE ALL
# =========================
def get_all_scans() -> list:
    """Returns all scan records newest-first; reasons deserialised to list."""
    try:
        with get_db_connection() as conn:
            cursor = conn.execute(
                'SELECT * FROM scan_history ORDER BY timestamp DESC'
            )
            rows = [dict(row) for row in cursor.fetchall()]
        for row in rows:
            row['reasons'] = json.loads(row['reasons']) if row['reasons'] else []
        return rows
    except sqlite3.Error as e:
        logger.error(f"❌ Retrieval failed: {e}")
        return []


# =========================
# DELETE ONE
# =========================
def delete_scan(scan_id: int):
    """Removes a single scan by primary key."""
    with get_db_connection() as conn:
        conn.execute('DELETE FROM scan_history WHERE id = ?', (scan_id,))
        conn.commit()
    logger.info(f"🗑  Scan {scan_id} deleted.")


# =========================
# DELETE ALL
# =========================
def delete_all_scans():
    """Wipes entire scan history."""
    with get_db_connection() as conn:
        conn.execute('DELETE FROM scan_history')
        conn.commit()
    logger.info("🗑  All scans deleted.")