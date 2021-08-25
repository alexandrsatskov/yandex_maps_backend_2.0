import pytest
from http import HTTPStatus

from analyzer.utils.testing import (
    get_user_feedbacks, post_user_feedbacks,
    get_visited_places, post_visited_places,
)
from analyzer.utils.generating_test_data import (
    generate_visited_place, generate_user_feedback,
)

LONGEST_STR = 'ё' * 256
CASES = (
    # Обработчик должен корректно добавлять запись места
    (
        generate_visited_place(),
        HTTPStatus.CREATED
    ),

    # Выгрузка с максимально длинными/большими значениями.
    # aiohttp должен разрешать запросы такого размера,
    # а обработчик не должен на них падать.
    (
        generate_visited_place(
            user_email=LONGEST_STR,
            place_uid=LONGEST_STR,
            place_id=999_999_999_999,
            longitude=180,
            latitude=90
        ),
        HTTPStatus.CREATED
    ),
)


@pytest.mark.parametrize('place,expected_status', CASES)
async def test_post_user_feedbacks(api_client, place, expected_status):
    # Заносим user_email и place_uid через ручку
    await post_visited_places(api_client, place)

    # Генерируем фидбек на основе вставленных данные
    feedback = generate_user_feedback(
        user_email=place.get('user_email', None),
        place_uid=place.get('place_uid', None)
    )
    await post_user_feedbacks(api_client, feedback)

    # Проверяем, что данные успешно импортированы
    if expected_status == HTTPStatus.CREATED:
        feedbacks = await get_user_feedbacks(
            api_client, user_email=place['user_email']
        )
        assert feedbacks == {'feedbacks': [feedback]}


async def test_get_non_existing_email_and_uid(api_client):
    # Если не существует user_email и place_uid в БД,
    # то фидбек не должен быть добавлен в БД
    feedback = generate_user_feedback()
    await post_user_feedbacks(api_client, feedback, HTTPStatus.BAD_REQUEST)


async def test_get_non_existing_email(api_client):
    # Если не существует user_email в БД,
    # то фидбек не должен быть добавлен в БД
    user_email = 'non_existing_email@yandex.ru'
    place = generate_visited_place()

    await post_visited_places(api_client, place)

    feedback = generate_user_feedback(
        user_email=user_email,
        place_uid=place['place_uid']
    )
    await post_user_feedbacks(api_client, feedback, HTTPStatus.BAD_REQUEST)


async def test_get_non_existing_uid(api_client):
    # Если не существует place_uid в БД,
    # то фидбек не должен быть добавлен в БД
    place_uid = 'non_existing_uid'
    place = generate_visited_place()

    await post_visited_places(api_client, place)

    feedback = generate_user_feedback(
        user_email=place['place_uid'],
        place_uid=place_uid
    )
    await post_user_feedbacks(api_client, feedback, HTTPStatus.BAD_REQUEST)
