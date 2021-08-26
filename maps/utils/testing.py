from enum import EnumMeta
from http import HTTPStatus
from typing import Any, Dict, Union
from urllib.parse import urlparse, urlencode, parse_qsl, urlunparse

from aiohttp.test_utils import TestClient
from pydantic import validate_model

from maps.api.handlers import (
    UserVisitedPlaces, UserFeedbacks
)
from maps.api.schema import (
    GetVisitedPlacesResponse, PostVisitedPlacesResponse,
    GetUserFeedbacksResponse, PostUserFeedbacksResponse,
)


def url_for(url: str, **params) -> str:
    """Генерирует URL с параметрами"""
    url_parse = urlparse(url)
    query = url_parse.query

    url_dict = dict(parse_qsl(query))
    url_dict.update(params)

    url_new_query = urlencode(url_dict)
    url_parse = url_parse._replace(query=url_new_query)
    new_url = urlunparse(url_parse)
    return new_url


async def post_visited_places(
    client: TestClient,
    place: Dict[str, Any],
    expected_status: Union[int, EnumMeta] = HTTPStatus.CREATED,
    **request_kwargs
):
    response = await client.post(
        UserVisitedPlaces.URL_PATH, json=place, **request_kwargs
    )
    assert response.status == expected_status

    if response.status == HTTPStatus.CREATED:
        data = await response.json()
        *_, errors = validate_model(PostVisitedPlacesResponse, data)
        assert errors is None, errors
        return data


async def post_user_feedbacks(
    client: TestClient,
    feedback: Dict[str, Any],
    expected_status: Union[int, EnumMeta] = HTTPStatus.CREATED,
    **request_kwargs
):
    response = await client.post(
        UserFeedbacks.URL_PATH, json=feedback, **request_kwargs
    )
    assert response.status == expected_status

    if response.status == HTTPStatus.CREATED:
        data = await response.json()
        *_, errors = validate_model(PostUserFeedbacksResponse, data)
        assert errors is None, errors
        return data


async def get_visited_places(
    client: TestClient,
    expected_status: Union[int, EnumMeta] = HTTPStatus.OK,
    **url_params
):
    response = await client.get(
        url_for(UserVisitedPlaces.URL_PATH, **url_params)
    )
    assert response.status == expected_status

    if response.status == HTTPStatus.OK:
        data = await response.json()
        *_, errors = validate_model(GetVisitedPlacesResponse, data)
        assert errors is None, errors
        return data


async def get_user_feedbacks(
    client: TestClient,
    expected_status: Union[int, EnumMeta] = HTTPStatus.OK,
    **url_params
):
    response = await client.get(
        url_for(UserFeedbacks.URL_PATH, **url_params)
    )
    assert response.status == expected_status

    if response.status == HTTPStatus.OK:
        data = await response.json()
        *_, errors = validate_model(GetUserFeedbacksResponse, data)
        assert errors is None, errors
        return data
