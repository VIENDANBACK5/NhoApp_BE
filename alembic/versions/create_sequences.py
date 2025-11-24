"""Create sequences and triggers for Oracle auto-increment

Revision ID: create_sequences
Revises: add_diary_features
Create Date: 2025-11-21 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'create_sequences'
down_revision = 'add_diary_features'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create sequences and triggers for all tables."""
    
    tables = [
        'users',
        'user_profiles',
        'diaries',
        'notes',
        'reminders',
        'memories',
        'health_logs',
        'conversations'
    ]
    
    conn = op.get_bind()
    
    for table_name in tables:
        sequence_name = f"{table_name}_seq"
        trigger_name = f"{table_name}_id_trigger"
        
        # Check if sequence exists
        result = conn.execute(sa.text(
            f"SELECT COUNT(*) FROM user_sequences WHERE sequence_name = UPPER('{sequence_name}')"
        ))
        if result.scalar() == 0:
            # Create sequence
            conn.execute(sa.text(
                f"CREATE SEQUENCE {sequence_name} START WITH 1 INCREMENT BY 1 NOCACHE NOCYCLE"
            ))
            conn.commit()
        
        # Check if trigger exists
        result = conn.execute(sa.text(
            f"SELECT COUNT(*) FROM user_triggers WHERE trigger_name = UPPER('{trigger_name}')"
        ))
        if result.scalar() == 0:
            # Create trigger for auto-increment
            trigger_sql = f"""
                CREATE OR REPLACE TRIGGER {trigger_name}
                BEFORE INSERT ON {table_name}
                FOR EACH ROW
                BEGIN
                    IF :new.id IS NULL THEN
                        SELECT {sequence_name}.NEXTVAL INTO :new.id FROM dual;
                    END IF;
                END;
            """
            # Use connection.exec_driver_sql to avoid bind parameter issues with :new
            conn.exec_driver_sql(trigger_sql)
            conn.commit()


def downgrade() -> None:
    """Drop sequences and triggers."""
    
    tables = [
        'users',
        'user_profiles',
        'diaries',
        'notes',
        'reminders',
        'memories',
        'health_logs',
        'conversations'
    ]
    
    conn = op.get_bind()
    
    for table_name in tables:
        sequence_name = f"{table_name}_seq"
        trigger_name = f"{table_name}_id_trigger"
        
        # Drop trigger
        try:
            conn.execute(sa.text(f"DROP TRIGGER {trigger_name}"))
            conn.commit()
        except:
            pass
        
        # Drop sequence
        try:
            conn.execute(sa.text(f"DROP SEQUENCE {sequence_name}"))
            conn.commit()
        except:
            pass
