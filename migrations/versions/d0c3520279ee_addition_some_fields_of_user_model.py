"""addition some fields of user model.

Revision ID: d0c3520279ee
Revises: 760dd63774cc
Create Date: 2020-04-15 20:40:28.981262

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd0c3520279ee'
down_revision = '760dd63774cc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('avatar_raw', sa.String(length=64), nullable=True))
    op.add_column('user', sa.Column('public_collections', sa.Boolean(), nullable=True))
    op.add_column('user', sa.Column('receive_collect_notification', sa.Boolean(), nullable=True))
    op.add_column('user', sa.Column('receive_comment_notification', sa.Boolean(), nullable=True))
    op.add_column('user', sa.Column('receive_follow_notification', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'receive_follow_notification')
    op.drop_column('user', 'receive_comment_notification')
    op.drop_column('user', 'receive_collect_notification')
    op.drop_column('user', 'public_collections')
    op.drop_column('user', 'avatar_raw')
    # ### end Alembic commands ###