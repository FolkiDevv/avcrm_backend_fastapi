"""remove on_delete from request_service_id

Revision ID: 5d9c8fe0ac57
Revises: 43cef753ebb4
Create Date: 2024-10-15 22:03:12.735665

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '5d9c8fe0ac57'
down_revision: Union[str, None] = '43cef753ebb4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('request_request_service_id_fkey', 'request', type_='foreignkey')
    op.create_foreign_key(None, 'request', 'request_service', ['request_service_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'request', type_='foreignkey')
    op.create_foreign_key('request_request_service_id_fkey', 'request', 'request_service', ['request_service_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###