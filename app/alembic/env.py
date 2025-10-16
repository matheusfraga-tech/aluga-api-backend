from __future__ import annotations
from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context
import sys
import os

# adiciona o path do projeto para encontrar os models
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# importa o Base e a URL do banco do seu projeto
from app.models import Base  # Base do __init__.py do pacote models
from app.database.database import DATABASE_URL

# Configuração do Alembic
config = context.config
fileConfig(config.config_file_name)

# garante que Alembic use a mesma URL que sua aplicação
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# metadata das tabelas
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = create_engine(
        DATABASE_URL,
        poolclass=pool.NullPool
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

