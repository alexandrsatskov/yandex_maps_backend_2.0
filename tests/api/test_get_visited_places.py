import pytest
from http import HTTPStatus

from maps.api.schema import UserContext
from maps.utils.testing import (
    get_user_feedbacks, post_user_feedbacks,
    get_visited_places, post_visited_places,
)
from maps.utils.generating_test_data import (
    generate_visited_place, generate_user_feedback,
)


@pytest.mark.parametrize('place', (
    # Обработчик должен корректно добавлять место
    generate_visited_place(),
))
async def test_get_visited_places(api_client, place):
    await post_visited_places(api_client, place)

    places = await get_visited_places(
        api_client,
        user_email=place['user_email'],
        user_context=UserContext.ugc.value,
        latitude=place['latitude'],
        longitude=place['longitude'],
    )
    place.update({'state': 3})
    place.pop('user_email')
    assert places == {'places': [place]}


async def test_get_non_existing_email(api_client):
    # Обработчик должен возвращать список дефолтных точек,
    # если идет обращение к несуществующему user_email
    # TODO: finish it up, dude
    user_email = 'non_existing_email@yandex.ru'
    await get_visited_places(
        api_client, user_email=user_email,
    )
