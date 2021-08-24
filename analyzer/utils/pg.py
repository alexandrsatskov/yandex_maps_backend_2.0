import logging
import os
from pathlib import Path
from types import SimpleNamespace
from typing import Union

from aiohttp.web_app import Application
from alembic.config import Config
from configargparse import Namespace
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

CENSORED = '***'
DEFAULT_PG_URL = 'postgresql+asyncpg://user:hackme@localhost/analyzer'
MAX_QUERY_ARGS = 32767
MAX_INTEGER = 2147483647

PROJECT_PATH = Path(__file__).parent.parent.resolve()


log = logging.getLogger(__name__)


async def setup_pg(app: Application, args: Namespace):
    db_info = args.pg_url.with_password(CENSORED)
    log.info('Connecting to database: %s', db_info)

    # TODO: fix args.pg_url
    # app['pg'] = create_async_engine(args.pg_url)
    app['pg'] = create_async_engine(
        DEFAULT_PG_URL,
        # echo=True
    )

    # Проверяем что база жива и отвечает
    async with app['pg'].connect() as conn:
        await conn.execute(text('SELECT 1'))
    log.info('Connected to database %s', db_info)

    yield
    log.info('Disconnecting from database %s', db_info)
    log.info('Disconnected from database %s', db_info)


def make_alembic_config(cmd_opts: Union[Namespace, SimpleNamespace],
                        base_path: str = PROJECT_PATH) -> Config:
    """
    Создает объект конфигурации alembic на основе аргументов командной строки,
    подменяет относительные пути на абсолютные.
    """
    # Подменяем путь до файла alembic.ini на абсолютный
    if not os.path.isabs(cmd_opts.config):
        cmd_opts.config = os.path.join(base_path, cmd_opts.config)

    config = Config(file_=cmd_opts.config, ini_section=cmd_opts.name,
                    cmd_opts=cmd_opts)

    # Подменяем путь до папки с alembic на абсолютный
    alembic_location = config.get_main_option('script_location')
    if not os.path.isabs(alembic_location):
        config.set_main_option('script_location',
                               os.path.join(base_path, alembic_location))
    if cmd_opts.pg_url:
        config.set_main_option('sqlalchemy.url', cmd_opts.pg_url)

    return config
