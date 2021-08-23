from http import HTTPStatus

import pytest

from analyzer.utils.pg import MAX_INTEGER
from analyzer.utils.testing import (
    generate_visited_place,
    generate_user_feedback,
    post_record, get_visited_places, get_user_feedbacks
)
from analyzer.api.handlers import UserFeedbacks, UserVisitedPlaces
from analyzer.api.schema import PostUserFeedbacksResponse, PostVisitedPlacesResponse, UserContext


CASES = (
    # Обработчик должен корректно добавлять запись места
    generate_visited_place(),
)


@pytest.mark.parametrize('place', CASES)
async def test_get_user_feedbacks(api_client, place):
    await post_record(
        api_client, place,
        UserVisitedPlaces, PostVisitedPlacesResponse,
        HTTPStatus.CREATED
    )

    feedback = generate_user_feedback(
        user_email=place['user_email'],
        place_uid=place['place_uid']
    )
    await post_record(
        api_client, feedback,
        UserFeedbacks, PostUserFeedbacksResponse,
        HTTPStatus.CREATED
    )

    feedbacks = await get_user_feedbacks(
        api_client, place['user_email']
    )

    assert feedbacks == [feedback]


async def test_get_non_existing_email(api_client):
    user_email = 'non_existing_email@yandex.ru'
    await get_user_feedbacks(
            api_client, user_email,
            expected_status=HTTPStatus.BAD_REQUEST
    )
