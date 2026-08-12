from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '3cfbd6b4515e'
down_revision: Union[str, Sequence[str], None] = '572a334f18e9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('employee_id', sa.String(), nullable=True))
    op.add_column('users', sa.Column('department', sa.String(), nullable=True))
    op.add_column('users', sa.Column('designation', sa.String(), nullable=True))
    op.add_column('users', sa.Column('phone_number', sa.String(), nullable=True))

    op.execute("""
        UPDATE users
        SET employee_id = 'EMP' || LPAD(id::text, 3, '0')
        WHERE employee_id IS NULL
    """)

    op.execute("""
        UPDATE users
        SET department = 'General'
        WHERE department IS NULL
    """)

    op.execute("""
        UPDATE users
        SET designation = 'Employee'
        WHERE designation IS NULL
    """)

    op.execute("""
        UPDATE users
        SET phone_number = '0000000000'
        WHERE phone_number IS NULL
    """)

    op.alter_column(
        'users',
        'employee_id',
        existing_type=sa.String(),
        nullable=False
    )

    op.alter_column(
        'users',
        'department',
        existing_type=sa.String(),
        nullable=False
    )

    op.alter_column(
        'users',
        'designation',
        existing_type=sa.String(),
        nullable=False
    )

    op.alter_column(
        'users',
        'phone_number',
        existing_type=sa.String(),
        nullable=False
    )

    op.create_unique_constraint(
        'uq_users_employee_id',
        'users',
        ['employee_id']
    )


def downgrade() -> None:
    op.drop_constraint(
        'uq_users_employee_id',
        'users',
        type_='unique'
    )

    op.drop_column('users', 'phone_number')
    op.drop_column('users', 'designation')
    op.drop_column('users', 'department')
    op.drop_column('users', 'employee_id')
