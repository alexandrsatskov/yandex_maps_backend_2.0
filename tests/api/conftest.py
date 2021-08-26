import pytest
from alembic.command import upgrade

from analyzer.api.__main__ import parser
from analyzer.api.app import create_app


@pytest.fixture
async def migrated_postgres(alembic_config, postgres):
    """
    Возвращает URL к БД с примененными миграциями.
    """
    upgrade(alembic_config, 'head')
    return postgres


@pytest.fixture
def arguments(aiomisc_unused_port, migrated_postgres):
    """
    Аргументы для запуска приложения.
    """
    return parser.parse_args(
        [
            '--log-level=debug',
            '--api-address=127.0.0.1',
            f'--api-port={aiomisc_unused_port}',
            f'--pg-url={str(migrated_postgres.async_.url)}'
        ]
    )


@pytest.fixture
async def api_client(aiohttp_client, arguments):
    app = create_app(arguments)
    client = await aiohttp_client(app, server_kwargs={
        'port': arguments.api_port
    })

    try:
        yield client
    finally:
        await client.close()
