"""Add data_source column to sos_signals table

Revision ID: 0001_add_data_source_to_sos_signal
Revises: None
Create Date: 2026-06-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_add_data_source_to_sos_signal'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add a nullable data_source column (works for SQLite and Postgres)
    op.add_column('sos_signals', sa.Column('data_source', sa.String(), nullable=True))


def downgrade():
    op.drop_column('sos_signals', 'data_source')
