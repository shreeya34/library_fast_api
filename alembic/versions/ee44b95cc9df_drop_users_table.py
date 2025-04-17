"""Drop users table

Revision ID: ee44b95cc9df
Revises: 
Create Date: 2025-04-11 09:57:56.629048

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ee44b95cc9df'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.drop_table('users')  

def downgrade():
    op.create_table(
        'users',
    )
