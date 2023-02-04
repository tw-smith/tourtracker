"""initial migration

Revision ID: b57a5ce1284e
Revises: 
Create Date: 2023-02-02 15:47:31.570352

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b57a5ce1284e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('uuid', sa.String(length=50), nullable=True),
    sa.Column('email', sa.String(length=50), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('verified', sa.Boolean(create_constraint=1), nullable=True),
    sa.Column('strava_athlete_id', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('uuid')
    )
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_user_strava_athlete_id'), ['strava_athlete_id'], unique=True)

    op.create_table('strava_access_token',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('athlete_id', sa.Integer(), nullable=True),
    sa.Column('access_token', sa.String(length=50), nullable=True),
    sa.Column('expires_at', sa.String(length=50), nullable=True),
    sa.ForeignKeyConstraint(['athlete_id'], ['user.strava_athlete_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('strava_access_token', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_strava_access_token_access_token'), ['access_token'], unique=False)
        batch_op.create_index(batch_op.f('ix_strava_access_token_athlete_id'), ['athlete_id'], unique=True)
        batch_op.create_index(batch_op.f('ix_strava_access_token_expires_at'), ['expires_at'], unique=False)

    op.create_table('strava_refresh_token',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('athlete_id', sa.Integer(), nullable=True),
    sa.Column('refresh_token', sa.String(length=50), nullable=True),
    sa.ForeignKeyConstraint(['athlete_id'], ['user.strava_athlete_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('strava_refresh_token', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_strava_refresh_token_athlete_id'), ['athlete_id'], unique=True)
        batch_op.create_index(batch_op.f('ix_strava_refresh_token_refresh_token'), ['refresh_token'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('strava_refresh_token', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_strava_refresh_token_refresh_token'))
        batch_op.drop_index(batch_op.f('ix_strava_refresh_token_athlete_id'))

    op.drop_table('strava_refresh_token')
    with op.batch_alter_table('strava_access_token', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_strava_access_token_expires_at'))
        batch_op.drop_index(batch_op.f('ix_strava_access_token_athlete_id'))
        batch_op.drop_index(batch_op.f('ix_strava_access_token_access_token'))

    op.drop_table('strava_access_token')
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_user_strava_athlete_id'))

    op.drop_table('user')
    # ### end Alembic commands ###
