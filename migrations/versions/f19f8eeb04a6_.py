"""empty message

Revision ID: f19f8eeb04a6
Revises: bf17116dfdfd
Create Date: 2020-03-30 16:15:48.236600

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f19f8eeb04a6'
down_revision = 'bf17116dfdfd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('permission_role_id_fkey', 'permission', type_='foreignkey')
    op.drop_column('permission', 'role_id')
    op.add_column('role', sa.Column('permission_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'role', 'permission', ['permission_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'role', type_='foreignkey')
    op.drop_column('role', 'permission_id')
    op.add_column('permission', sa.Column('role_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('permission_role_id_fkey', 'permission', 'role', ['role_id'], ['id'])
    # ### end Alembic commands ###