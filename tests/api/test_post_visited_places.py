import pytest
from http import HTTPStatus

from maps.api.schema import UserContext
from maps.utils.testing import (
    get_visited_places, post_visited_places,
)
from maps.utils.generating_test_data import (
    generate_visited_place,
)


# TODO: find problem with 'ё'
LONGEST_STR = 'a' * 256
CASES = (
    # Обработчик должен корректно добавлять запись места
    (
        generate_visited_place(latitude=1, longitude=1),
        HTTPStatus.CREATED
    ),

    # Выгрузка с максимально длинными/большими значениями.
    # aiohttp должен разрешать запросы такого размера,
    # а обработчик не должен на них падать.
    (
        generate_visited_place(
            user_email=LONGEST_STR,
            place_uid=LONGEST_STR,
            place_id=999999999999,
            longitude=1,
            latitude=-1
        ),
        HTTPStatus.CREATED
    ),

    # Пустая выгрузка
    # Обработчик не должен падать на таких данных.
    (
        {},
        HTTPStatus.BAD_REQUEST
    ),
)


@pytest.mark.parametrize('place,expected_status', CASES)
async def test_post_visited_places(api_client, place, expected_status):
    result = await post_visited_places(api_client, place, expected_status)

    # Проверяем, что данные успешно импортированы
    if expected_status == HTTPStatus.CREATED:
        assert result['place_uid'] == place['place_uid']

        places = await get_visited_places(api_client, user_email=place['user_email'])

        place.update({'state': 3})
        place.pop('user_email')
        assert places == {'places': [place]}
