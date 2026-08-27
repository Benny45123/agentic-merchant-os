import os
import sqlite3
from pathlib import Path
from alembic.config import Config
from alembic import command


def test_migrations_run_clean_and_downgrade(tmp_path: Path):
    """Verifies that Alembic migrations run cleanly up to head and downgrade back to base."""
    db_file = tmp_path / "test_migration.db"
    db_url = f"sqlite+aiosqlite:///{db_file}"
    
    # Path to alembic.ini
    backend_dir = Path(__file__).resolve().parent.parent
    alembic_ini_path = backend_dir / "alembic.ini"
    
    alembic_cfg = Config(str(alembic_ini_path))
    alembic_cfg.set_main_option("script_location", str(backend_dir / "alembic"))
    alembic_cfg.set_main_option("sqlalchemy.url", db_url)
    alembic_cfg.set_section_option("alembic", "sqlalchemy.url", db_url)

    # Use environment variable override for test db url
    os.environ["DATABASE_URL"] = db_url
    
    try:
        command.upgrade(alembic_cfg, "head")
        
        # Verify tables exist using standard sqlite3
        conn = sqlite3.connect(str(db_file))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        expected_tables = [
            "merchants",
            "buyers",
            "products",
            "catalog_snapshots",
            "mandates",
            "merchant_policies",
            "campaign_policies",
            "transaction_intents",
            "guardian_decisions",
            "campaigns",
            "offers",
            "campaign_events",
            "orders",
            "payments",
            "receipts",
        ]
        for expected in expected_tables:
            assert expected in tables, f"Expected table '{expected}' was not created by migration"
            
        # Test downgrade to base
        command.downgrade(alembic_cfg, "base")
        
        # Verify tables dropped
        conn = sqlite3.connect(str(db_file))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables_after = [row[0] for row in cursor.fetchall() if not row[0].startswith("alembic_")]
        conn.close()
        
        assert len(tables_after) == 0, f"Expected all tables dropped on downgrade base, found: {tables_after}"
    finally:
        os.environ.pop("DATABASE_URL", None)
