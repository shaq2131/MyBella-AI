"""
Migration: Add profile preference columns for modern onboarding
Adds nickname, pronouns, support_focus, support_topics, and check_in_preference
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend import create_app
from backend.database.models.models import db


def add_column(conn, statement, label):
    try:
        conn.execute(db.text(statement))
        print(f"✓ Added {label} column")
    except Exception as exc:  # pylint: disable=broad-except
        message = str(exc).lower()
        if "duplicate" in message or "exists" in message:
            print(f"✓ {label} column already exists")
        else:
            print(f"⚠️  Could not add {label} column: {exc}")


def run_migration():
    app, _ = create_app()
    with app.app_context():
        with db.engine.connect() as conn:
            add_column(conn, "ALTER TABLE user_settings ADD COLUMN nickname VARCHAR(100)", "nickname")
            add_column(conn, "ALTER TABLE user_settings ADD COLUMN pronouns VARCHAR(50)", "pronouns")
            add_column(conn, "ALTER TABLE user_settings ADD COLUMN support_focus VARCHAR(50)", "support_focus")
            add_column(conn, "ALTER TABLE user_settings ADD COLUMN support_topics TEXT", "support_topics")
            add_column(conn, "ALTER TABLE user_settings ADD COLUMN check_in_preference VARCHAR(50)", "check_in_preference")
            conn.commit()
        print("\n✅ Profile preference migration complete")


if __name__ == "__main__":
    print("🚀 Starting profile preference migration...\n")
    run_migration()
