import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool, create_engine
from alembic import context
from app.core.database import Base 
from app.models.user import User 
from app.models.perfil import UserMateria
from app.models.enums import CondicionLaboral

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# --- NUEVA VARIABLE ---
# Leemos la URL aquí mismo desde el entorno
DATABASE_URL_ENV = os.environ.get("DATABASE_URL")
# --------------------

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    
    # --- CAMBIO ---
    url = DATABASE_URL_ENV # Usamos nuestra variable
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    # -------------

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    
    # --- CAMBIO ---
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = DATABASE_URL_ENV # Usamos nuestra variable
    connectable = create_engine(configuration["sqlalchemy.url"])
    # -------------

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()