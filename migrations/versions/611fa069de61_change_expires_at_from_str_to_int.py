"""change expires_at from str to int

Revision ID: 611fa069de61
Revises: b57a5ce1284e
Create Date: 2023-02-02 16:11:57.599506

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '611fa069de61'
down_revision = 'b57a5ce1284e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('strava_access_token', schema=None) as batch_op:
        batch_op.alter_column('expires_at',
               existing_type=sa.VARCHAR(length=50),
               type_=sa.Integer(),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('strava_access_token', schema=None) as batch_op:
        batch_op.alter_column('expires_at',
               existing_type=sa.Integer(),
               type_=sa.VARCHAR(length=50),
               existing_nullable=True)

    # ### end Alembic commands ###
