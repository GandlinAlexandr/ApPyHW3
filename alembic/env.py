from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from config import SYNC_DATABASE_URL as DATABASE_URL
from database import Base
from auth.db import User
from database import ExpiredLink

print("RAW DATABASE_URL bytes:", list(DATABASE_URL.encode("utf-8", errors="replace")))

# Подключаем конфиг Alembic
alembic_config  = context.config

alembic_config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Настройка логирования
if alembic_config.config_file_name is not None:
    fileConfig(alembic_config.config_file_name)

target_metadata = Base.metadata  # Указываем метаданные моделей

def run_migrations_offline() -> None:
    """Запуск миграций в 'offline' режиме."""
    url = alembic_config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Запуск миграций в 'online' режиме."""
    connectable = engine_from_config(
        alembic_config.get_section(alembic_config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
