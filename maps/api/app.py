import logging
from functools import partial

from aiohttp.web_app import Application
from configargparse import Namespace
from aiohttp_pydantic import oas

from maps.api.handlers import HANDLERS
from maps.api.middleware import error_middleware
from maps.utils.pg import setup_pg


log = logging.getLogger(__name__)


def create_app(args: Namespace) -> Application:

    app = Application(
        middlewares=[error_middleware],
    )

    # Подключение на старте к postgres и отключение при остановке
    app.cleanup_ctx.append(partial(setup_pg, args=args))

    for handler in HANDLERS:
        log.debug('Registering handler %r as %r', handler, handler.URL_PATH)
        app.router.add_route('*', handler.URL_PATH, handler)

    # Swagger документация
    oas.setup(app, url_prefix="/docs")
    return app
