import pytest
from http import HTTPStatus

from analyzer.utils.testing import (
    get_user_feedbacks, post_user_feedbacks,
    get_visited_places, post_visited_places,
)
from analyzer.utils.generating_test_data import (
    generate_visited_place, generate_user_feedback,
)


@pytest.mark.parametrize('place', (
    # Обработчик должен корректно добавлять место
    generate_visited_place(),
))
async def test_get_user_feedbacks(api_client, place):
    # Заносим user_email и place_uid через ручку
    await post_visited_places(api_client, place)

    # Генерируем фидбек на основе вставленных данные
    feedback = generate_user_feedback(
        user_email=place.get('user_email', None),
        place_uid=place.get('place_uid', None)
    )
    await post_user_feedbacks(api_client, feedback)

    feedbacks = await get_user_feedbacks(
        api_client, user_email=place['user_email']
    )

    assert feedbacks == {'feedbacks': [feedback]}


async def test_get_non_existing_email(api_client):
    user_email = 'non_existing_email@yandex.ruabs'
    await get_user_feedbacks(
        api_client, HTTPStatus.BAD_REQUEST, user_email=user_email,
    )
