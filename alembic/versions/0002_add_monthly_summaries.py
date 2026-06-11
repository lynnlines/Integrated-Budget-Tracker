from alembic import op
import sqlalchemy as sa

revision = "0002_add_monthly_summaries"
down_revision = "0001_initial"
branch_labels = None

def upgrade():
    op.create_table(
        "monthly_summaries",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("account_id", sa.String(length=36), nullable=True),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("month", sa.Integer(), nullable=False),
        sa.Column("total_spent_cents", sa.BigInteger(), nullable=False),
        sa.Column("total_income_cents", sa.BigInteger(), nullable=False),
        sa.Column("per_category", sa.JSON(), nullable=True),
        sa.Column("generated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    )
    op.create_index("ix_monthly_summaries_year_month", "monthly_summaries", ["year", "month"], unique=False)


def downgrade():
    op.drop_index("ix_monthly_summaries_year_month", table_name="monthly_summaries")
    op.drop_table("monthly_summaries")
