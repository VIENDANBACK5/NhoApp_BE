"""add memory media fields

Revision ID: 20251123_231646
Revises: create_sequences
Create Date: 2025-11-23 23:16:46

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251123_231646'
down_revision = 'create_sequences'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add image_url and audio_url columns to memories table"""
    op.add_column('memories', sa.Column('image_url', sa.String(length=500), nullable=True))
    op.add_column('memories', sa.Column('audio_url', sa.String(length=500), nullable=True))


def downgrade() -> None:
    """Remove image_url and audio_url columns from memories table"""
    op.drop_column('memories', 'audio_url')
    op.drop_column('memories', 'image_url')
