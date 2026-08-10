"""FastMCP CRM Server - exposes mock CRM tools backed by SQLite."""

import os
import sqlite3
from pathlib import Path

from fastmcp import FastMCP

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
DB_PATH = DATA_DIR / "crm.db"

mcp = FastMCP("SalesFlow CRM", description="Mock CRM tools for sales agent demo")


def _get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


@mcp.tool()
def list_top_deals(limit: int = 5) -> list[dict]:
    """List top deals by value, returning deal name, amount, and stage."""
    conn = _get_db()
    try:
        cursor = conn.execute(
            "SELECT name, amount, stage FROM deals ORDER BY amount DESC LIMIT ?",
            (limit,),
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


@mcp.tool()
def get_forecast(quarter: str) -> dict:
    """Get sales forecast for a given quarter (e.g., 'Q3')."""
    conn = _get_db()
    try:
        cursor = conn.execute(
            "SELECT quarter, amount, category, confidence FROM forecasts WHERE quarter = ?",
            (quarter,),
        )
        rows = [dict(row) for row in cursor.fetchall()]
        if not rows:
            return {"quarter": quarter, "message": "No forecast data available"}
        total = sum(r["amount"] for r in rows)
        return {
            "quarter": quarter,
            "total_forecast": total,
            "categories": rows,
        }
    finally:
        conn.close()


@mcp.tool()
def search_accounts(query: str) -> list[dict]:
    """Search accounts by name or industry."""
    conn = _get_db()
    try:
        cursor = conn.execute(
            "SELECT name, industry, size, revenue FROM accounts WHERE name LIKE ? OR industry LIKE ?",
            (f"%{query}%", f"%{query}%"),
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


@mcp.tool()
def get_contacts(account_name: str) -> list[dict]:
    """Get contacts for a given account name."""
    conn = _get_db()
    try:
        cursor = conn.execute(
            """SELECT c.name, c.title, c.email 
               FROM contacts c JOIN accounts a ON c.account_id = a.id 
               WHERE a.name LIKE ?""",
            (f"%{account_name}%",),
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


@mcp.tool()
def get_pipeline_summary() -> dict:
    """Get a summary of the current sales pipeline by stage."""
    conn = _get_db()
    try:
        cursor = conn.execute(
            "SELECT stage, COUNT(*) as count, SUM(amount) as total FROM deals GROUP BY stage"
        )
        stages = [dict(row) for row in cursor.fetchall()]
        total_value = sum(s["total"] for s in stages)
        total_deals = sum(s["count"] for s in stages)
        return {
            "total_deals": total_deals,
            "total_value": total_value,
            "by_stage": stages,
        }
    finally:
        conn.close()


if __name__ == "__main__":
    port = int(os.environ.get("MCP_SERVER_PORT", "8001"))
    mcp.run(transport="streamable-http", host="127.0.0.1", port=port)
