import logging
from functools import partial

from aiohttp.web_app import Application
from aiohttp_pydantic import oas
from configargparse import Namespace

from analyzer.api.handlers import HANDLERS
from analyzer.api.middleware import error_middleware
from analyzer.utils.pg import setup_pg
from analyzer.utils.monkey_patching_aiohttp_pydantic import _add_http_method_to_oas

# По умолчанию размер запроса к aiohttp ограничен 1 мегабайтом:
# https://docs.aiohttp.org/en/stable/web_reference.html#aiohttp.web.Application
# Размер запроса со 10 000 жителей и 2000 связей (с учетом максимальной длины
# строк и кодировки json с параметром ensure_ascii=True) может занимать
# ~63 мегабайт:
MEGABYTE = 1024 ** 2
MAX_REQUEST_SIZE = 70 * MEGABYTE

log = logging.getLogger(__name__)


def create_app(args: Namespace) -> Application:
    """
    Создает экземпляр приложения, готового к запуску.
    """
    # [START] monkey patching
    oas.view._add_http_method_to_oas = _add_http_method_to_oas
    # [END] monkey patching

    app = Application(
        client_max_size=MAX_REQUEST_SIZE,
        middlewares=[error_middleware]
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
