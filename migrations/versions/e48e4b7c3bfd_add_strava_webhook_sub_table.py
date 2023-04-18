"""add strava webhook sub table

Revision ID: e48e4b7c3bfd
Revises: 4bdb05b0439b
Create Date: 2023-04-17 19:48:21.695322

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e48e4b7c3bfd'
down_revision = '4bdb05b0439b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('strava_webhook_subscription',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('subscription_id', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('strava_webhook_subscription', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_strava_webhook_subscription_subscription_id'), ['subscription_id'], unique=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('strava_webhook_subscription', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_strava_webhook_subscription_subscription_id'))

    op.drop_table('strava_webhook_subscription')
    # ### end Alembic commands ###
