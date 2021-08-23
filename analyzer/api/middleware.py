import logging
import json
from http import HTTPStatus
from typing import Any, Mapping, Optional
from functools import partial, singledispatch

from aiohttp.typedefs import JSONEncoder
from aiohttp.payload import JsonPayload as BaseJsonPayload
from aiohttp.web_exceptions import (
    HTTPException, HTTPInternalServerError,
    HTTPNotFound, HTTPFound
)
from aiohttp.web import json_response
from aiohttp.web_middlewares import middleware
from aiohttp.web_request import Request

from analyzer.api.schema import ErrorResponseSchema


log = logging.getLogger(__name__)


dumps = partial(json.dumps, ensure_ascii=False)
class JsonPayload(BaseJsonPayload):
    """
    Заменяет функцию сериализации на более "умную" (умеющую упаковывать в JSON
    объекты asyncpg.Record и другие сущности).
    """
    def __init__(self,
                 value: Any,
                 encoding: str = 'utf-8',
                 content_type: str = 'application/json',
                 dumps: JSONEncoder = dumps,
                 *args: Any,
                 **kwargs: Any) -> None:
        super().__init__(value, encoding, content_type, dumps, *args, **kwargs)


def format_http_error(http_error_cls, message: Optional[str] = None,
                      fields: Optional[Mapping] = None):
    """
    Форматирует ошибку в виде HTTP исключения
    """
    status = HTTPStatus(http_error_cls.status_code)
    error = {
        'code': f'{http_error_cls.status_code} {status.name}',
        'message': message or status.description
    }

    if fields is not None:
        error['fields'] = fields

    return http_error_cls(body={'error': error})



@middleware
async def error_middleware(request: Request, handler):
    try:
        return await handler(request)
    except HTTPNotFound:
        raise HTTPFound('/docs')
    except HTTPException as err:
        # Исключения которые представляют из себя HTTP ответ, были брошены
        # осознанно для отображения клиенту.
        if not isinstance(err.body, JsonPayload):
            err = format_http_error(err.__class__, err.text)

        raise err

    except Exception:
        # Все остальные исключения не могут быть отображены клиенту в виде
        # HTTP ответа и могут случайно раскрыть внутреннюю информацию.
        log.exception('Unhandled exception')
        raise format_http_error(HTTPInternalServerError)
