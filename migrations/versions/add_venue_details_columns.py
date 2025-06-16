"""add venue details columns

Revision ID: add_venue_details_columns
Revises: None
Create Date: 2024-02-14 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_venue_details_columns'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns to owners table
    op.add_column('owners', sa.Column('google_maps_link', sa.String(500), nullable=True))
    op.add_column('owners', sa.Column('amenities', sa.Text, nullable=True))
    op.add_column('owners', sa.Column('venue_image1', sa.String(500), nullable=True))
    op.add_column('owners', sa.Column('venue_image2', sa.String(500), nullable=True))
    op.add_column('owners', sa.Column('venue_image3', sa.String(500), nullable=True))
    op.add_column('owners', sa.Column('venue_image4', sa.String(500), nullable=True))
    op.add_column('owners', sa.Column('images_uploaded', sa.Boolean, server_default='0', nullable=False))


def downgrade():
    # Remove columns from owners table
    op.drop_column('owners', 'images_uploaded')
    op.drop_column('owners', 'venue_image4')
    op.drop_column('owners', 'venue_image3')
    op.drop_column('owners', 'venue_image2')
    op.drop_column('owners', 'venue_image1')
    op.drop_column('owners', 'amenities')
    op.drop_column('owners', 'google_maps_link')