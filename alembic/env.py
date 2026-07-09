from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool

from backend.src.config.database import engine, Base

import backend.src.models.auth
import backend.src.models.category
import backend.src.models.enterprise
import backend.src.models.expert
import backend.src.models.project
import backend.src.models.proposal
import backend.src.models.review

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline():
    context.configure(
        url=str(engine.url),
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    with engine.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()