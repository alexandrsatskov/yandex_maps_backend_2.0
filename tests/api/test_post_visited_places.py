from http import HTTPStatus

import pytest

from analyzer.utils.pg import MAX_INTEGER
from analyzer.utils.testing import (
    generate_visited_place,
    post_record, get_visited_places
)
from analyzer.api.handlers import UserVisitedPlaces
from analyzer.api.schema import PostVisitedPlacesResponse, UserContext


LONGEST_STR = 'ё' * (256 // 128)
CASES = (
    # Обработчик должен корректно добавлять запись места
    (
        generate_visited_place(
            user_email=LONGEST_STR,
            place_uid=LONGEST_STR,
            place_id=999_999_999_999,
            longitude=180,
            latitude=-90
        ),
        HTTPStatus.CREATED
    ),

    # Выгрузка с максимально длинными/большими значениями.
    # aiohttp должен разрешать запросы такого размера,
    # а обработчик не должен на них падать.
    (
        generate_visited_place(),
        HTTPStatus.CREATED
    ),

    # Пустая выгрузка
    # Обработчик не должен падать на таких данных.
    (
        {},
        HTTPStatus.BAD_REQUEST
    ),

    # citizen_id не уникален в рамках выгрузки
    # (
    #     [
    #         generate_citizen(citizen_id=1),
    #         generate_citizen(citizen_id=1),
    #     ],
    #     HTTPStatus.BAD_REQUEST
    # ),
)


@pytest.mark.parametrize('place,expected_status', CASES)
async def test_post_visited_places(api_client, place, expected_status):
    res = await post_record(
        api_client, place,
        UserVisitedPlaces, PostVisitedPlacesResponse,
        expected_status
    )

    # Проверяем, что данные успешно импортированы
    if expected_status == HTTPStatus.CREATED:
        assert res['place_uid'] == place['place_uid']
        visited_places = await get_visited_places(
            api_client, user_email=place['user_email'], user_context=UserContext.ugc.value,
            latitude=place['latitude'], longitude=place['longitude'],
            expected_status=HTTPStatus.OK
        )
        visited_places.pop('state')
        place.pop('user_email')
        assert visited_places == place
