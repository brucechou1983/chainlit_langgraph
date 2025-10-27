"""add_missing_columns_props_and_defaultOpen

Revision ID: de67071c2f5e
Revises: e2a0c10ab218
Create Date: 2025-10-27 19:42:12.109282

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'de67071c2f5e'
down_revision: Union[str, None] = 'e2a0c10ab218'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add missing 'props' column to elements table
    op.add_column('elements', sa.Column('props', postgresql.JSONB(astext_type=sa.Text()), nullable=True))

    # Add missing 'defaultOpen' column to steps table
    op.add_column('steps', sa.Column('defaultOpen', sa.Boolean(), nullable=False, server_default='false'))


def downgrade() -> None:
    # Remove columns in reverse order
    op.drop_column('steps', 'defaultOpen')
    op.drop_column('elements', 'props')
