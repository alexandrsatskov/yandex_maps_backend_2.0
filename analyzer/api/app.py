import logging
from functools import partial

from aiohttp.web_app import Application
from configargparse import Namespace

from analyzer.api.handlers import HANDLERS
from analyzer.api.middleware import error_middleware
from analyzer.utils.pg import setup_pg
from analyzer.utils.monkey_patching_aiohttp_pydantic import (
    _add_http_method_to_oas, inject_params
)

log = logging.getLogger(__name__)


def create_app(args: Namespace) -> Application:
    """
    Создает экземпляр приложения, готового к запуску.
    """
    # [START] monkey patching
    from aiohttp_pydantic import oas
    from aiohttp_pydantic import view
    oas.view._add_http_method_to_oas = _add_http_method_to_oas
    view.inject_params = inject_params
    # [END] monkey patching

    app = Application(
        middlewares=[error_middleware],
    )

    # Подключение на старте к postgres и отключение при остановке
    app.cleanup_ctx.append(partial(setup_pg, args=args))

    # TODO: fix it up, dude
    for handler in HANDLERS:
        log.debug('Registering handler %r as %r', handler, handler.URL_PATH)
        app.router.add_route('*', handler.URL_PATH, handler)

    # Swagger документация
    oas.setup(app, url_prefix="/docs")
    return app
