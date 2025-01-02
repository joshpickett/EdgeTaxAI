"""create tax code table

Revision ID: a1b2c3d4e5f6
Revises: previous_revision_id
Create Date: 2024-01-20 10:00:00.000000

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision = "previous_revision_id"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "tax_code",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(10), nullable=False),
        sa.Column("section", sa.String(20), nullable=False),
        sa.Column("subsection", sa.String(20)),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("full_text", sa.Text(), nullable=False),
        sa.Column("keywords", sa.Text()),
        sa.Column(
            "last_updated", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.add_column("tax_payments", sa.Column("tax_code_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_tax_payments_tax_code", "tax_payments", "tax_code", ["tax_code_id"], ["id"]
    )


def downgrade():
    op.drop_constraint("fk_tax_payments_tax_code", "tax_payments", type_="foreignkey")
    op.drop_column("tax_payments", "tax_code_id")
    op.drop_table("tax_code")
