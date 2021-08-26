import logging
from http import HTTPStatus
from typing import Optional, Mapping

from aiohttp.web_exceptions import (
    HTTPException, HTTPFound,
    HTTPInternalServerError,
    HTTPBadRequest
)
from aiohttp.web import json_response
from aiohttp.web_middlewares import middleware
from aiohttp.web_request import Request
from pydantic import ValidationError

log = logging.getLogger(__name__)


def format_http_error(http_error_cls, message: Optional[str] = None,
                      fields: Optional[Mapping] = None):
    """
    Форматирует ошибку в виде HTTP исключения
    """
    status = HTTPStatus(http_error_cls.status_code)
    error = {
        'code': f'{status.value} {status.phrase}',
        'message': message or status.description
    }

    if fields:
        error['fields'] = fields

    return json_response({'error': error}, status=status.value)


def handle_validation_error(error: ValidationError, *_):
    """
    Представляет ошибку валидации данных в виде HTTP ответа.
    """
    return format_http_error(HTTPBadRequest, 'Request validation has failed', error.errors())


@middleware
async def error_middleware(request: Request, handler):
    try:
        return await handler(request)

    except HTTPException as err:
        if err.status_code == 404:
            # Автоматический редирект на документацию
            raise HTTPFound('/docs')

        return format_http_error(err.__class__, err.text)

    except ValidationError as err:
        # Ошибки валидации, брошенные в обработчиках
        return handle_validation_error(err)

    except Exception:
        # Все остальные исключения не могут быть отображены клиенту в виде
        # HTTP ответа и могут случайно раскрыть внутреннюю информацию.
        log.exception('Unhandled exception')
        return format_http_error(HTTPInternalServerError)
