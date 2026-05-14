"""add hnsw index on resume_chunks embedding

Revision ID: 1ea44c8d6888
Revises: 51ef048d1c1e
Create Date: 2026-05-14 11:42:40.736420

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1ea44c8d6888'
down_revision: Union[str, None] = '51ef048d1c1e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "CREATE INDEX ix_resume_chunks_embedding_hnsw "
        "ON resume_chunks USING hnsw (embedding vector_cosine_ops)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_resume_chunks_embedding_hnsw")
