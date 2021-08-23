from http import HTTPStatus

import pytest

from analyzer.utils.pg import MAX_INTEGER
from analyzer.utils.testing import (
    generate_visited_place, generate_user_feedback,
    post_record, get_visited_places, get_user_feedbacks
)
from analyzer.api.handlers import UserVisitedPlaces, UserFeedbacks
from analyzer.api.schema import PostVisitedPlacesResponse, UserContext, PostUserFeedbacksResponse


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

    # Пустая выгрузка
    # Обработчик не должен падать на таких данных.
    (
        {},
        HTTPStatus.BAD_REQUEST
    ),
)


@pytest.mark.parametrize('place,expected_status', CASES)
async def test_post_user_feedbacks(api_client, place, expected_status):
    res = await post_record(
        api_client, place,
        UserVisitedPlaces, PostVisitedPlacesResponse,
        expected_status
    )
    feedback = generate_user_feedback(
        place.get('user_email', None), place.get('place_uid', None)
    )
    res = await post_record(
        api_client, feedback,
        UserFeedbacks, PostUserFeedbacksResponse,
        expected_status
    )

    # Проверяем, что данные успешно импортированы
    if expected_status == HTTPStatus.CREATED:
        user_feedbacks = await get_user_feedbacks(
            api_client, place['user_email']
        )
        assert user_feedbacks == [feedback]


async def test_get_non_existing_email_and_uid(api_client):
    feedback = generate_user_feedback()
    await post_record(
        api_client, feedback,
        UserFeedbacks, PostUserFeedbacksResponse,
        HTTPStatus.BAD_REQUEST
    )


async def test_get_non_existing_email(api_client):
    user_email = 'non_existing_email@yandex.ru'
    place = generate_visited_place()

    await post_record(
        api_client, place,
        UserVisitedPlaces, PostVisitedPlacesResponse,
        HTTPStatus.CREATED
    )

    feedback = generate_user_feedback(
        user_email=user_email,
        place_uid=place['place_uid']
    )
    await post_record(
        api_client, feedback,
        UserFeedbacks, PostUserFeedbacksResponse,
        HTTPStatus.BAD_REQUEST
    )


async def test_get_non_existing_uid(api_client):
    place_uid = 'non_existing_uid'
    place = generate_visited_place()

    await post_record(
        api_client, place,
        UserVisitedPlaces, PostVisitedPlacesResponse,
        HTTPStatus.CREATED
    )

    feedback = generate_user_feedback(
        user_email=place['user_email'],
        place_uid=place_uid
    )
    await post_record(
        api_client, feedback,
        UserFeedbacks, PostUserFeedbacksResponse,
        HTTPStatus.BAD_REQUEST
    )
