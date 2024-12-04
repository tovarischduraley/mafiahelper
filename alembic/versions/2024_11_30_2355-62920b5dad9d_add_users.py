"""add_users

Revision ID: 62920b5dad9d
Revises: cee64bcb7603
Create Date: 2024-11-30 23:55:09.372408

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '62920b5dad9d'
down_revision: Union[str, None] = 'cee64bcb7603'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.rename_table("users", "players")
    op.alter_column("users_games", "user_id", new_column_name="player_id")
    op.rename_table("users_games", "players_games")
    op.drop_constraint(constraint_name="users_games_game_id_fkey", table_name="players_games", type_="foreignkey")
    op.drop_constraint(constraint_name="users_games_user_id_fkey", table_name="players_games", type_="foreignkey")
    op.create_foreign_key(None, "players_games", "players", ["player_id"], ["id"])
    op.create_foreign_key(None, "players_games", "games", ["game_id"], ["id"])
    op.create_table(
        "users",
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("first_name", sa.String(), nullable=False),
        sa.Column("last_name", sa.String(), nullable=True),
        sa.Column("username", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("telegram_id"),
    )


def downgrade() -> None:
    op.drop_table("users")
    op.alter_column("players_games", "player_id", new_column_name="user_id")
    op.drop_constraint(constraint_name="players_games_player_id_fkey", table_name="players_games", type_="foreignkey")
    op.drop_constraint(constraint_name="players_games_game_id_fkey", table_name="players_games", type_="foreignkey")
    op.rename_table("players_games", "users_games")
    op.rename_table("players", "users")
    op.create_foreign_key(
        constraint_name=None,
        source_table="users_games",
        referent_table="users",
        local_cols=["user_id"],
        remote_cols=["id"],
    )
    op.create_foreign_key(
        constraint_name=None,
        source_table="users_games",
        referent_table="games",
        local_cols=["game_id"],
        remote_cols=["id"],
    )
