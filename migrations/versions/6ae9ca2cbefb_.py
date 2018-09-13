"""
As per wireframe requirement created sample table

Revision ID: 6ae9ca2cbefb
Revises: 0440e03bc8e2
Create Date: 2018-04-05 16:45:19.424463

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '6ae9ca2cbefb'
down_revision = '0440e03bc8e2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('samples',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('sample_id', sa.String(length=100), nullable=False),
    sa.Column('tissue_type', sa.String(length=50), nullable=False),
    sa.Column('site', sa.String(length=50), nullable=False),
    sa.Column('gender', sa.String(length=10), nullable=False),
    sa.Column('metastatic_site', sa.String(length=10), nullable=False),
    sa.Column('cancer', sa.String(length=100), nullable=False),
    sa.Column('EGFR', sa.Boolean(), nullable=False),
    sa.Column('IDH1', sa.Boolean(), nullable=False),
    sa.Column('IDH2', sa.Boolean(), nullable=False),
    sa.Column('TP53', sa.Boolean(), nullable=False),
    sa.Column('age_in_year', sa.Integer(), nullable=True),
    sa.Column('tumor_grade', sa.String(length=100), nullable=True),
    sa.Column('tumor_stage', sa.String(length=100), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column(u'job', sa.Column('sample_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'job', 'samples', ['sample_id'], ['id'], ondelete='cascade')
    op.drop_column(u'job', 'disease_name')
    op.drop_column(u'job', 'mutation_gene')
    op.drop_column(u'job', 'gdc_project_id')
    op.drop_column(u'job', 'site')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(u'job', sa.Column('site', mysql.VARCHAR(length=255), nullable=False))
    op.add_column(u'job', sa.Column('gdc_project_id', mysql.VARCHAR(length=50), nullable=False))
    op.add_column(u'job', sa.Column('mutation_gene', mysql.VARCHAR(length=100), nullable=False))
    op.add_column(u'job', sa.Column('disease_name', mysql.VARCHAR(length=100), nullable=False))
    op.drop_constraint(None, 'job', type_='foreignkey')
    op.drop_column(u'job', 'sample_id')
    op.drop_table('samples')
    # ### end Alembic commands ###
