"""Phase 2 production readiness: particle filtering, calibration, DB indexes

Revision ID: 002_phase2_improvements
Revises: 001_phase1_improvements
Create Date: 2026-09-17 14:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '002_phase2_improvements'
down_revision: Union[str, None] = '001_phase1_improvements'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add filtering and calibration columns to analyses table
    with op.batch_alter_table('analyses', schema=None) as batch_op:
        batch_op.add_column(sa.Column('total_detected_objects', sa.Integer(), nullable=True, server_default='0'))
        batch_op.add_column(sa.Column('valid_particles', sa.Integer(), nullable=True, server_default='0'))
        batch_op.add_column(sa.Column('filtered_objects', sa.Integer(), nullable=True, server_default='0'))
        batch_op.add_column(sa.Column('pixel_size_um', sa.Float(), nullable=True))
        batch_op.create_index('ix_analyses_created_at', ['created_at'], unique=False)

    # Add index on created_at for evaluations table
    with op.batch_alter_table('evaluations', schema=None) as batch_op:
        batch_op.create_index('ix_evaluations_created_at', ['created_at'], unique=False)


def downgrade() -> None:
    with op.batch_alter_table('evaluations', schema=None) as batch_op:
        batch_op.drop_index('ix_evaluations_created_at')

    with op.batch_alter_table('analyses', schema=None) as batch_op:
        batch_op.drop_index('ix_analyses_created_at')
        batch_op.drop_column('pixel_size_um')
        batch_op.drop_column('filtered_objects')
        batch_op.drop_column('valid_particles')
        batch_op.drop_column('total_detected_objects')
