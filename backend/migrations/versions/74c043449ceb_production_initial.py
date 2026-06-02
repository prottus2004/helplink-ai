"""production_initial

Revision ID: 74c043449ceb
Revises: 0001_initial_schema
Create Date: 2026-06-01 13:08:22.463519
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '74c043449ceb'
down_revision = '0001_initial_schema'
branch_labels = None
depends_on = None


def upgrade():
    # Tables are created by create_all_tables() in main.py _safe_startup()
    # This migration is a marker only — stamp "head" records this version
    pass


def downgrade():
    # No-op: tables are managed by create_all_tables(), not by alembic
    pass
