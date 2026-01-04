"""add_phase_v_schema_extensions

Revision ID: 7e2870cc7002
Revises: 5aad0ce77300
Create Date: 2025-12-30 15:41:53.484305

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7e2870cc7002'
down_revision: Union[str, Sequence[str], None] = '5aad0ce77300'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add new columns to tasks table for Phase V
    op.add_column('tasks', sa.Column('priority', sa.String(length=10), server_default='Medium', nullable=False))
    op.add_column('tasks', sa.Column('tags', sa.ARRAY(sa.String()), server_default='{}', nullable=False))
    op.add_column('tasks', sa.Column('due_date', sa.DateTime(), nullable=True))
    op.add_column('tasks', sa.Column('recurrence_pattern', sa.String(length=20), server_default='none', nullable=False))
    op.add_column('tasks', sa.Column('reminder_lead_time', sa.Integer(), nullable=True))

    # Add CHECK constraints for enums
    op.create_check_constraint(
        'tasks_priority_check',
        'tasks',
        "priority IN ('High', 'Medium', 'Low')"
    )
    op.create_check_constraint(
        'tasks_recurrence_pattern_check',
        'tasks',
        "recurrence_pattern IN ('none', 'daily', 'weekly', 'monthly')"
    )

    # Add indexes for Phase V columns
    op.create_index('idx_tasks_priority', 'tasks', ['priority'])
    op.create_index('idx_tasks_tags', 'tasks', ['tags'], postgresql_using='gin')
    op.create_index('idx_tasks_due_date', 'tasks', ['due_date'])
    op.create_index(
        'idx_tasks_recurrence',
        'tasks',
        ['recurrence_pattern'],
        postgresql_where="recurrence_pattern != 'none'"
    )

    # Create task_events table
    op.create_table(
        'task_events',
        sa.Column('event_id', sa.String(), nullable=False),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('task_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('published_to_kafka', sa.Boolean(), server_default='FALSE', nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('event_id')
    )
    op.create_index('idx_task_events_task_id', 'task_events', ['task_id'])
    op.create_index('idx_task_events_user_id', 'task_events', ['user_id'])
    op.create_index('idx_task_events_timestamp', 'task_events', ['timestamp'], postgresql_ops={'timestamp': 'DESC'})
    op.create_index('idx_task_events_type', 'task_events', ['event_type'])

    # Create recurring_task_schedules table
    op.create_table(
        'recurring_task_schedules',
        sa.Column('schedule_id', sa.String(), nullable=False),
        sa.Column('parent_task_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('recurrence_pattern', sa.String(length=20), nullable=False),
        sa.Column('next_execution_time', sa.DateTime(), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='TRUE', nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('last_executed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('schedule_id'),
        sa.ForeignKeyConstraint(['parent_task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('parent_task_id')
    )
    op.create_index(
        'idx_schedules_next_execution',
        'recurring_task_schedules',
        ['next_execution_time'],
        postgresql_where='is_active = TRUE'
    )
    op.create_index('idx_schedules_user', 'recurring_task_schedules', ['user_id'])

    # Create notifications table
    op.create_table(
        'notifications',
        sa.Column('notification_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('task_id', sa.String(), nullable=True),
        sa.Column('notification_type', sa.String(length=50), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('sent_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('delivery_status', sa.String(length=20), server_default='sent', nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('notification_id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='SET NULL')
    )
    op.create_index('idx_notifications_user_status', 'notifications', ['user_id', 'delivery_status'])
    op.create_index('idx_notifications_sent_at', 'notifications', ['sent_at'], postgresql_ops={'sent_at': 'DESC'})

    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('audit_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('action_type', sa.String(length=50), nullable=False),
        sa.Column('resource_type', sa.String(length=50), server_default='task', nullable=False),
        sa.Column('resource_id', sa.String(), nullable=False),
        sa.Column('event_data', sa.JSON(), nullable=False),
        sa.Column('correlation_id', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('audit_id')
    )
    op.create_index('idx_audit_user', 'audit_logs', ['user_id'])
    op.create_index('idx_audit_resource', 'audit_logs', ['resource_id'])
    op.create_index('idx_audit_timestamp', 'audit_logs', ['timestamp'], postgresql_ops={'timestamp': 'DESC'})
    op.create_index('idx_audit_correlation', 'audit_logs', ['correlation_id'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop audit_logs table
    op.drop_index('idx_audit_correlation', 'audit_logs')
    op.drop_index('idx_audit_timestamp', 'audit_logs')
    op.drop_index('idx_audit_resource', 'audit_logs')
    op.drop_index('idx_audit_user', 'audit_logs')
    op.drop_table('audit_logs')

    # Drop notifications table
    op.drop_index('idx_notifications_sent_at', 'notifications')
    op.drop_index('idx_notifications_user_status', 'notifications')
    op.drop_table('notifications')

    # Drop recurring_task_schedules table
    op.drop_index('idx_schedules_user', 'recurring_task_schedules')
    op.drop_index('idx_schedules_next_execution', 'recurring_task_schedules')
    op.drop_table('recurring_task_schedules')

    # Drop task_events table
    op.drop_index('idx_task_events_type', 'task_events')
    op.drop_index('idx_task_events_timestamp', 'task_events')
    op.drop_index('idx_task_events_user_id', 'task_events')
    op.drop_index('idx_task_events_task_id', 'task_events')
    op.drop_table('task_events')

    # Drop indexes and constraints from tasks table
    op.drop_index('idx_tasks_recurrence', 'tasks')
    op.drop_index('idx_tasks_due_date', 'tasks')
    op.drop_index('idx_tasks_tags', 'tasks')
    op.drop_index('idx_tasks_priority', 'tasks')
    op.drop_constraint('tasks_recurrence_pattern_check', 'tasks')
    op.drop_constraint('tasks_priority_check', 'tasks')

    # Drop new columns from tasks table
    op.drop_column('tasks', 'reminder_lead_time')
    op.drop_column('tasks', 'recurrence_pattern')
    op.drop_column('tasks', 'due_date')
    op.drop_column('tasks', 'tags')
    op.drop_column('tasks', 'priority')
