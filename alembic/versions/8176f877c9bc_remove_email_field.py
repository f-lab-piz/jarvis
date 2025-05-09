"""Remove email field

Revision ID: 8176f877c9bc
Revises: 866a41058068
Create Date: 2025-05-04 14:18:30.522890

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8176f877c9bc'
down_revision: Union[str, None] = '866a41058068'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_users_email', table_name='users')
    op.drop_column('users', 'email')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('email', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    # ### end Alembic commands ###
