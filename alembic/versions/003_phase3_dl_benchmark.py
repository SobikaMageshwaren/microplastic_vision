"""Phase 3 deep learning benchmark: model registry table

Revision ID: 003_phase3_dl_benchmark
Revises: 002_phase2_improvements
Create Date: 2026-09-17 15:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '003_phase3_dl_benchmark'
down_revision: Union[str, None] = '002_phase2_improvements'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'model_registry',
        sa.Column('model_id', sa.String(length=50), nullable=False),
        sa.Column('model_name', sa.String(length=255), nullable=False),
        sa.Column('architecture', sa.String(length=50), nullable=True),
        sa.Column('version', sa.String(length=50), nullable=True),
        sa.Column('checkpoint_path', sa.Text(), nullable=False),
        sa.Column('configuration_hash', sa.String(length=64), nullable=True),
        sa.Column('dataset_split_json', sa.JSON(), nullable=True),
        sa.Column('metrics_json', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('model_id')
    )
    op.create_index(op.f('ix_model_registry_model_id'), 'model_registry', ['model_id'], unique=False)
    op.create_index(op.f('ix_model_registry_configuration_hash'), 'model_registry', ['configuration_hash'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_model_registry_configuration_hash'), table_name='model_registry')
    op.drop_index(op.f('ix_model_registry_model_id'), table_name='model_registry')
    op.drop_table('model_registry')
