"""Phase 1 essential improvements: evaluations, experiments, configuration hash

Revision ID: 001_phase1_improvements
Revises: 
Create Date: 2026-09-17 14:15:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_phase1_improvements'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add configuration columns to analyses table if they don't exist
    with op.batch_alter_table('analyses', schema=None) as batch_op:
        batch_op.add_column(sa.Column('configuration_hash', sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column('configuration_json', sa.JSON(), nullable=True))
        batch_op.create_index(batch_op.f('ix_analyses_configuration_hash'), ['configuration_hash'], unique=False)

    # Create evaluations table
    op.create_table(
        'evaluations',
        sa.Column('evaluation_id', sa.String(length=50), nullable=False),
        sa.Column('analysis_id', sa.String(length=50), nullable=True),
        sa.Column('image_name', sa.String(length=255), nullable=False),
        sa.Column('iou', sa.Float(), nullable=False),
        sa.Column('dice', sa.Float(), nullable=False),
        sa.Column('precision', sa.Float(), nullable=False),
        sa.Column('recall', sa.Float(), nullable=False),
        sa.Column('f1', sa.Float(), nullable=False),
        sa.Column('tp_pixels', sa.Integer(), nullable=True),
        sa.Column('fp_pixels', sa.Integer(), nullable=True),
        sa.Column('fn_pixels', sa.Integer(), nullable=True),
        sa.Column('tn_pixels', sa.Integer(), nullable=True),
        sa.Column('predicted_particle_count', sa.Integer(), nullable=True),
        sa.Column('ground_truth_particle_count', sa.Integer(), nullable=True),
        sa.Column('particle_count_error', sa.Integer(), nullable=True),
        sa.Column('processing_time_ms', sa.Float(), nullable=True),
        sa.Column('error_map_path', sa.Text(), nullable=True),
        sa.Column('overlay_path', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('evaluation_id')
    )
    op.create_index(op.f('ix_evaluations_evaluation_id'), 'evaluations', ['evaluation_id'], unique=False)
    op.create_index(op.f('ix_evaluations_analysis_id'), 'evaluations', ['analysis_id'], unique=False)

    # Create experiments table
    op.create_table(
        'experiments',
        sa.Column('experiment_id', sa.String(length=50), nullable=False),
        sa.Column('experiment_type', sa.String(length=50), nullable=True),
        sa.Column('experiment_name', sa.String(length=255), nullable=False),
        sa.Column('pipeline_version', sa.String(length=50), nullable=True),
        sa.Column('configuration_hash', sa.String(length=64), nullable=True),
        sa.Column('configuration_json', sa.JSON(), nullable=True),
        sa.Column('metrics_json', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('experiment_id')
    )
    op.create_index(op.f('ix_experiments_experiment_id'), 'experiments', ['experiment_id'], unique=False)
    op.create_index(op.f('ix_experiments_experiment_type'), 'experiments', ['experiment_type'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_experiments_experiment_type'), table_name='experiments')
    op.drop_index(op.f('ix_experiments_experiment_id'), table_name='experiments')
    op.drop_table('experiments')

    op.drop_index(op.f('ix_evaluations_analysis_id'), table_name='evaluations')
    op.drop_index(op.f('ix_evaluations_evaluation_id'), table_name='evaluations')
    op.drop_table('evaluations')

    with op.batch_alter_table('analyses', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_analyses_configuration_hash'))
        batch_op.drop_column('configuration_json')
        batch_op.drop_column('configuration_hash')
