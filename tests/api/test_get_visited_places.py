import asyncio
from http import HTTPStatus

import pytest

from analyzer.utils.pg import MAX_INTEGER
from analyzer.utils.testing import (
    generate_visited_place,
    post_record, get_visited_places
)
from analyzer.api.handlers import UserVisitedPlaces
from analyzer.api.schema import PostVisitedPlacesResponse, UserContext


CASES = (
    # Обработчик должен корректно добавлять запись места
    generate_visited_place(),

    # citizen_id не уникален в рамках выгрузки
    # (
    #     [
    #         generate_citizen(citizen_id=1),
    #         generate_citizen(citizen_id=1),
    #     ],
    #     HTTPStatus.BAD_REQUEST
    # ),
)


@pytest.mark.parametrize('place', CASES)
async def test_get_visited_places(api_client, place):
    await post_record(
        api_client, place,
        UserVisitedPlaces, PostVisitedPlacesResponse,
        HTTPStatus.CREATED
    )

    visited_places = await get_visited_places(
        api_client, user_email=place['user_email'], user_context=UserContext.ugc.value,
        latitude=place['latitude'], longitude=place['longitude'],
        expected_status=HTTPStatus.OK
    )
    visited_places.pop('state')
    place.pop('user_email')
    assert visited_places == place


async def test_get_non_existing_email(api_client):
    user_email = 'non_existing_email@yandex.ru'
    await get_visited_places(
            api_client, user_email, UserContext.ugc.value,
            expected_status=HTTPStatus.BAD_REQUEST
        )
