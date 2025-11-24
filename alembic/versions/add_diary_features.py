"""
Migration: Add Diary, Note, Memory, Health features

Tạo các bảng:
- diaries: Nhật ký cá nhân
- notes: Ghi chú thông minh
- reminders: Nhắc nhở tự động
- memories: Ký ức cá nhân
- health_logs: Nhật ký sức khỏe
- conversations: Lịch sử chat AI
- user_profiles: Thông tin chi tiết người dùng
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_diary_features'
down_revision = 'initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade schema."""
    
    # User Profiles Table
    op.create_table(
        'user_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('full_name', sa.String(100), nullable=True),
        sa.Column('age', sa.Integer(), nullable=True),
        sa.Column('birth_date', sa.Date(), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('emergency_contact', sa.String(100), nullable=True),
        sa.Column('medical_conditions', sa.Text(), nullable=True, server_default='[]'),
        sa.Column('medications', sa.Text(), nullable=True, server_default='[]'),
        sa.Column('allergies', sa.Text(), nullable=True, server_default='[]'),
        sa.Column('hobbies', sa.Text(), nullable=True, server_default='[]'),
        sa.Column('important_dates', sa.Text(), nullable=True, server_default='[]'),
        sa.Column('daily_routine', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('SYSDATE')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('SYSDATE')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index('ix_user_profiles_user_id', 'user_profiles', ['user_id'])
    
    # Diaries Table
    op.create_table(
        'diaries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('emotion', sa.String(50), nullable=True),
        sa.Column('image_url', sa.String(500), nullable=True),
        sa.Column('entry_type', sa.String(20), nullable=False, server_default='diary'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('SYSDATE')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('SYSDATE')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_diaries_user_id', 'diaries', ['user_id'])
    op.create_index('ix_diaries_created_at', 'diaries', ['created_at'])
    
    # Notes Table
    op.create_table(
        'notes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('category', sa.String(50), nullable=True),
        sa.Column('extracted_datetime', sa.DateTime(), nullable=True),
        sa.Column('priority', sa.String(20), nullable=False, server_default='medium'),
        sa.Column('is_reminder', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('SYSDATE')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('SYSDATE')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_notes_user_id', 'notes', ['user_id'])
    op.create_index('ix_notes_category', 'notes', ['category'])
    
    # Reminders Table
    op.create_table(
        'reminders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('note_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('remind_at', sa.DateTime(), nullable=False),
        sa.Column('is_completed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('SYSDATE')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('SYSDATE')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['note_id'], ['notes.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_reminders_user_id', 'reminders', ['user_id'])
    op.create_index('ix_reminders_remind_at', 'reminders', ['remind_at'])
    op.create_index('ix_reminders_is_completed', 'reminders', ['is_completed'])
    
    # Memories Table
    op.create_table(
        'memories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('tags', sa.Text(), nullable=True, server_default='[]'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('SYSDATE')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('SYSDATE')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_memories_user_id', 'memories', ['user_id'])
    
    # Health Logs Table
    op.create_table(
        'health_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('log_type', sa.String(50), nullable=False),
        sa.Column('value', sa.String(100), nullable=False),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('SYSDATE')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('SYSDATE')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_health_logs_user_id', 'health_logs', ['user_id'])
    op.create_index('ix_health_logs_log_type', 'health_logs', ['log_type'])
    
    # Conversations Table
    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('messages', sa.Text(), nullable=True, server_default='[]'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('SYSDATE')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('SYSDATE')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_conversations_user_id', 'conversations', ['user_id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_conversations_user_id', table_name='conversations')
    op.drop_table('conversations')
    
    op.drop_index('ix_health_logs_log_type', table_name='health_logs')
    op.drop_index('ix_health_logs_user_id', table_name='health_logs')
    op.drop_table('health_logs')
    
    op.drop_index('ix_memories_user_id', table_name='memories')
    op.drop_table('memories')
    
    op.drop_index('ix_reminders_is_completed', table_name='reminders')
    op.drop_index('ix_reminders_remind_at', table_name='reminders')
    op.drop_index('ix_reminders_user_id', table_name='reminders')
    op.drop_table('reminders')
    
    op.drop_index('ix_notes_category', table_name='notes')
    op.drop_index('ix_notes_user_id', table_name='notes')
    op.drop_table('notes')
    
    op.drop_index('ix_diaries_created_at', table_name='diaries')
    op.drop_index('ix_diaries_user_id', table_name='diaries')
    op.drop_table('diaries')
    
    op.drop_index('ix_user_profiles_user_id', table_name='user_profiles')
    op.drop_table('user_profiles')
