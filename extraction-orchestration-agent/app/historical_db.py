"""
===============================================================================
🏛️ WORKSHOP STARTER: Group A - Historical Baseline & Looped Learning DB
===============================================================================
This module handles asynchronous SQLite persistence for:
1. Vendor Historical Baselines (`vendor_baselines` table)
2. Looped Learning Human Reviews (`human_reviews` table)
===============================================================================
"""

import aiosqlite
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "historical_contracts.db")


async def init_db():
    """Initializes historical vendor baseline table and looped learning review store."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS vendor_baselines (
                vendor_name TEXT PRIMARY KEY,
                avg_contract_value REAL,
                max_historical_liability TEXT,
                avg_insurance_amount REAL,
                total_past_contracts INTEGER
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS human_reviews (
                case_id TEXT PRIMARY KEY,
                vendor_name TEXT,
                flagged_risk TEXT,
                human_action TEXT,
                reviewer_comments TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await db.execute("""
            INSERT OR IGNORE INTO vendor_baselines (vendor_name, avg_contract_value, max_historical_liability, avg_insurance_amount, total_past_contracts)
            VALUES 
                ('Acme Corp', 350000.0, 'limited', 2000000.0, 5),
                ('Globex Logistics', 150000.0, 'limited', 1000000.0, 3),
                ('Initech Software', 600000.0, 'limited', 5000000.0, 8)
        """)
        await db.commit()


async def get_vendor_baseline(vendor_name: str) -> dict:
    """Retrieves historical baseline for a vendor."""
    await init_db()
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT avg_contract_value, max_historical_liability, avg_insurance_amount, total_past_contracts FROM vendor_baselines WHERE vendor_name = ?",
            (vendor_name,),
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return {
                    "vendor_name": vendor_name,
                    "avg_contract_value": row[0],
                    "max_historical_liability": row[1],
                    "avg_insurance_amount": row[2],
                    "total_past_contracts": row[3],
                }

            return {
                "vendor_name": vendor_name,
                "avg_contract_value": 250000.0,
                "max_historical_liability": "limited",
                "avg_insurance_amount": 1000000.0,
                "total_past_contracts": 0,
            }


async def save_human_review(
    case_id: str,
    vendor_name: str,
    flagged_risk: str,
    human_action: str,
    comments: str,
    approved_contract_value: float = 0.0,
):
    """Stores human reviewer override and recalibrates vendor baseline thresholds."""
    await init_db()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT OR REPLACE INTO human_reviews (case_id, vendor_name, flagged_risk, human_action, reviewer_comments)
            VALUES (?, ?, ?, ?, ?)
            """,
            (case_id, vendor_name, flagged_risk, human_action, comments),
        )

        if human_action in ["OVERRIDDEN", "APPROVED"] and approved_contract_value > 0:
            baseline = await get_vendor_baseline(vendor_name)
            old_avg = baseline["avg_contract_value"]
            past_count = baseline["total_past_contracts"]

            new_count = past_count + 1
            new_avg = round(((old_avg * past_count) + approved_contract_value) / new_count, 2)

            await db.execute(
                """
                UPDATE vendor_baselines
                SET avg_contract_value = ?, total_past_contracts = ?
                WHERE vendor_name = ?
                """,
                (new_avg, new_count, vendor_name),
            )

        await db.commit()
