"""Add ML analysis fields to tasks

Revision ID: 0001
Revises: 
Create Date: 2025-09-27 17:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types
    tree_type_enum = postgresql.ENUM('oak', 'pine', 'birch', 'maple', 'cherry', 'unknown', name='treetype')
    damage_type_enum = postgresql.ENUM('insect_damage', 'fungal_infection', 'bark_damage', 'leaf_discoloration', 'branch_breakage', 'root_damage', 'drought_stress', 'nutrient_deficiency', name='damagetype')
    
    tree_type_enum.create(op.get_bind())
    damage_type_enum.create(op.get_bind())
    
    # Add new columns to tasks table
    op.add_column('tasks', sa.Column('tree_type', tree_type_enum, nullable=True))
    op.add_column('tasks', sa.Column('tree_type_confidence', sa.Float(), nullable=True))
    op.add_column('tasks', sa.Column('damages_detected', sa.Text(), nullable=True))
    op.add_column('tasks', sa.Column('overall_health_score', sa.Float(), nullable=True))


def downgrade() -> None:
    # Remove columns
    op.drop_column('tasks', 'overall_health_score')
    op.drop_column('tasks', 'damages_detected')
    op.drop_column('tasks', 'tree_type_confidence')
    op.drop_column('tasks', 'tree_type')
    
    # Drop enum types
    op.execute('DROP TYPE IF EXISTS treetype')
    op.execute('DROP TYPE IF EXISTS damagetype')
