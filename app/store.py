import sqlite3
import logging
from datetime import datetime, timezone
from typing import Optional

from app.config import DATABASE_PATH
from app.models import YelpLead, LeadRecord

logger = logging.getLogger(__name__)


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = _connect()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            job_type TEXT,
            zip_code TEXT,
            message TEXT,
            survey_answers TEXT,
            image_urls TEXT,
            lead_created_at TEXT,
            response_text TEXT,
            status TEXT NOT NULL DEFAULT 'new',
            created_at TEXT NOT NULL,
            responded_at TEXT
        )
    """)
    conn.commit()
    conn.close()
    logger.info("Database ready at %s", DATABASE_PATH)


def save_lead(lead: YelpLead) -> int:
    conn = _connect()
    cursor = conn.execute(
        """INSERT INTO leads
           (customer_name, job_type, zip_code, message, survey_answers,
            image_urls, lead_created_at, status, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, 'new', ?)""",
        (
            lead.customer_name,
            lead.job_type,
            lead.zip_code,
            lead.message,
            lead.survey_answers,
            lead.image_urls,
            lead.lead_created_at,
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    conn.commit()
    lead_id = cursor.lastrowid
    conn.close()
    return lead_id


def update_lead_response(lead_id: int, response_text: str) -> None:
    conn = _connect()
    conn.execute(
        """UPDATE leads
           SET response_text = ?, status = 'responded', responded_at = ?
           WHERE id = ?""",
        (response_text, datetime.now(timezone.utc).isoformat(), lead_id),
    )
    conn.commit()
    conn.close()


def get_lead(lead_id: int) -> Optional[dict]:
    conn = _connect()
    row = conn.execute("SELECT * FROM leads WHERE id = ?", (lead_id,)).fetchone()
    conn.close()
    if row is None:
        return None
    return dict(row)


def get_all_leads() -> list[dict]:
    conn = _connect()
    rows = conn.execute("SELECT * FROM leads ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]
