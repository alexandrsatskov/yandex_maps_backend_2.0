import os
import uuid
from types import SimpleNamespace
from dataclasses import dataclass

import pytest
from yarl import URL
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy_utils import create_database, drop_database

from maps.utils.pg import DEFAULT_PG_URL, make_alembic_config

PG_URL = os.getenv('CI_MAPS_PG_URL', DEFAULT_PG_URL)


@dataclass
class PostgresEngine:
    """
    Создаем два engine к базе: синхронный и асинхронный
    Тесты использует асинхронный engine, однако мы
    вынуждены использовать сихнронный вариант для
    создания/удаления БД методами sqlalchemy_utils, а
    так же для применения миграций с помощью alembic
    обе эти библиотеки умеют работать лишь в sync mode
    """
    # Убираем префикс с асинхронным драйвером
    sync: Engine = create_engine(PG_URL.replace('+asyncpg', ''))
    async_: AsyncEngine = create_async_engine(PG_URL)


@pytest.fixture
def postgres():
    """
    Создает временную БД для запуска теста.
    """
    pg_engine = PostgresEngine()

    tmp_name = '.'.join([uuid.uuid4().hex, 'pytest'])
    tmp_url = str(URL(str(pg_engine.sync.url)).with_path(tmp_name))

    create_database(tmp_url)

    # Устанавливаем PostGis
    # from sqlalchemy import text
    # with pg_engine.sync.connect() as connection:
    #     connection.execute(text("CREATE EXTENSION postgis;"))

    try:
        yield pg_engine
    finally:
        drop_database(tmp_url)


@pytest.fixture()
def alembic_config(postgres):
    """
    Создает объект с конфигурацией для alembic, настроенный на временную БД.
    """
    cmd_options = SimpleNamespace(config='alembic.ini', name='alembic',
                                  pg_url=str(postgres.sync.url), raiseerr=False, x=None)
    return make_alembic_config(cmd_options)
