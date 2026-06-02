"""Initial schema - create all tables

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-06-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = '0001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # sos_signals table
    op.create_table('sos_signals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source', sa.String(), nullable=True),
        sa.Column('raw_message', sa.Text(), nullable=False),
        sa.Column('language_detected', sa.String(), nullable=True),
        sa.Column('language_confidence', sa.Float(), nullable=True),
        sa.Column('has_survivor_signal', sa.Boolean(), nullable=True),
        sa.Column('survivor_count_estimate', sa.Integer(), nullable=True),
        sa.Column('location_extracted', sa.String(), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('priority_score', sa.Float(), nullable=True),
        sa.Column('priority_level', sa.String(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=True),
        sa.Column('data_source', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sos_signals_id'), 'sos_signals', ['id'], unique=False)

    # rescue_teams table
    op.create_table('rescue_teams',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('team_name', sa.String(), nullable=False),
        sa.Column('team_code', sa.String(), nullable=False),
        sa.Column('unit_type', sa.String(), nullable=True),
        sa.Column('current_lat', sa.Float(), nullable=False),
        sa.Column('current_lng', sa.Float(), nullable=False),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('assigned_signal_id', sa.Integer(), nullable=True),
        sa.Column('personnel_count', sa.Integer(), nullable=True),
        sa.Column('last_updated', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['assigned_signal_id'], ['sos_signals.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rescue_teams_id'), 'rescue_teams', ['id'], unique=False)
    op.create_index(op.f('ix_rescue_teams_team_code'), 'rescue_teams', ['team_code'], unique=True)

    # satellite_zones table
    op.create_table('satellite_zones',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('zone_name', sa.String(), nullable=False),
        sa.Column('center_lat', sa.Float(), nullable=False),
        sa.Column('center_lng', sa.Float(), nullable=False),
        sa.Column('flood_severity', sa.Float(), nullable=True),
        sa.Column('area_sqkm', sa.Float(), nullable=True),
        sa.Column('isolated_structures', sa.Integer(), nullable=True),
        sa.Column('water_depth_estimate', sa.Float(), nullable=True),
        sa.Column('scenario_id', sa.String(), nullable=False),
        sa.Column('last_updated', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_satellite_zones_id'), 'satellite_zones', ['id'], unique=False)

    # cellular_anomalies table
    op.create_table('cellular_anomalies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tower_id', sa.String(), nullable=False),
        sa.Column('lat', sa.Float(), nullable=False),
        sa.Column('lng', sa.Float(), nullable=False),
        sa.Column('anomaly_type', sa.String(), nullable=True),
        sa.Column('anomaly_score', sa.Float(), nullable=True),
        sa.Column('affected_radius_km', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cellular_anomalies_id'), 'cellular_anomalies', ['id'], unique=False)

    # demo_scenarios table
    op.create_table('demo_scenarios',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('scenario_name', sa.String(), nullable=False),
        sa.Column('location', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('disaster_type', sa.String(), nullable=True),
        sa.Column('severity', sa.String(), nullable=True),
        sa.Column('total_affected', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_demo_scenarios_id'), 'demo_scenarios', ['id'], unique=False)


def downgrade():
    op.drop_table('demo_scenarios')
    op.drop_table('cellular_anomalies')
    op.drop_table('satellite_zones')
    op.drop_table('rescue_teams')
    op.drop_table('sos_signals')
