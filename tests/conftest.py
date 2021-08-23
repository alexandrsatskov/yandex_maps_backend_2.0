import os
import uuid
from types import SimpleNamespace

import pytest
from yarl import URL
from sqlalchemy import create_engine, text
from sqlalchemy_utils import (
    create_database, drop_database,
    render_expression, render_statement
)

from analyzer.utils.pg import DEFAULT_PG_URL, make_alembic_config


PG_URL = os.getenv('CI_ANALYZER_PG_URL', DEFAULT_PG_URL)


@pytest.fixture
def postgres():
    """
    Создает временную БД для запуска теста.
    """
    # Убираем префикс с асинхронным драйвером, т.к.
    # sqlalchemy_utils умеют только в sync mode
    sync_url = PG_URL.replace('+asyncpg', '')

    tmp_name = '.'.join([uuid.uuid4().hex, 'pytest'])
    tmp_url = str(URL(sync_url).with_path(tmp_name))

    create_database(tmp_url)
    engine = create_engine(tmp_url)

    # Устанавливаем postgis extension
    with engine.connect() as connection:
        connection.execute(text("CREATE EXTENSION postgis;"))

    try:
        yield tmp_url
    finally:
        drop_database(tmp_url)


@pytest.fixture()
def alembic_config(postgres):
    """
    Создает объект с конфигурацией для alembic, настроенный на временную БД.
    """
    cmd_options = SimpleNamespace(config='alembic.ini', name='alembic',
                                  pg_url=postgres, raiseerr=False, x=None)
    return make_alembic_config(cmd_options)
