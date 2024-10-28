"""user_login and user_login_succeed

Revision ID: 7fa0fca70702
Revises: 00e5de83d7c3
Create Date: 2024-10-22 14:36:49.302447

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '7fa0fca70702'
down_revision: Union[str, None] = '00e5de83d7c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_login',
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('attempts', sa.Integer(), nullable=False),
    sa.Column('last_attempt_at', sa.DateTime(), nullable=False),
    sa.Column('blocked_before', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id')
    )
    op.create_table('user_login_succeed',
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('agent_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_login_succeed_id'), 'user_login_succeed', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_login_succeed_id'), table_name='user_login_succeed')
    op.drop_table('user_login_succeed')
    op.drop_table('user_login')
    # ### end Alembic commands ###