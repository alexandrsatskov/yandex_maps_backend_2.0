import logging
from typing import Optional, List, Dict, Any

from aiohttp.web_exceptions import (
    HTTPException, HTTPFound,
    HTTPInternalServerError,
)
from aiohttp.web import json_response
from aiohttp.web_middlewares import middleware
from aiohttp.web_request import Request
from pydantic import ValidationError

log = logging.getLogger(__name__)


def format_http_error(
    reason, text: Optional[str] = None,
    fields: Optional[List[Dict[str, Any]]] = None,
    **kwargs
):
    error_template = {"error": {
        "reason": reason,
    }}

    if text is not None:
        error_template['error'].update({"text": text})

    if fields is not None:
        error_template['error'].update({"fields": fields})

    return json_response(error_template, **kwargs)


@middleware
async def error_middleware(request: Request, handler):
    try:
        return await handler(request)

    except ValidationError as err:
        # Ошибки валидации, брошенные в обработчиках
        return format_http_error(
            reason=f'400 Bad request',
            text="Request validation has failed",
            fields=err.errors(),
            status=400
        )

    except HTTPException as err:
        if err.status_code == 404:
            # Автоматический редирект на документацию
            raise HTTPFound('/docs')

        if err.status_code == 500:
            log.exception('Internal error')
            return format_http_error(f'{err.status_code} {err.reason}', status=500)

    except Exception as err:
        # Все остальные исключения не могут быть отображены клиенту в виде
        # HTTP ответа и могут случайно раскрыть внутреннюю информацию.
        log.exception('Unhandled exception %s', err)
        return format_http_error('500 Unhandled exception', status=500)
