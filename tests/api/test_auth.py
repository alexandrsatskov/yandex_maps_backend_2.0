import http

import pytest

from maps.api.handlers import (
    UserVisitedPlaces, UserFeedbacks
)
from maps.utils.testing import (
    get_user_feedbacks, post_user_feedbacks,
    get_visited_places, post_visited_places,
    delete_user_feedbacks, url_for
)
from maps.utils.generating_test_data import (
    generate_visited_place, generate_user_feedback,
)

# Нужно проверить что ручки работают через валидный токен
# Нужно проверить что ручки не работают через невалидный токен
# Нужно проверить что ручки не работаю через не переданный токен

TOKEN = 'AQAAAABTLcs3AAdIB1io1O_Ko0KDirq2Kt7GZIw'


async def test_valid_token(api_client):
    place = generate_visited_place()

    user_email = place['user_email']
    place_uid = place['place_uid']

    feedback = generate_user_feedback(
        user_email=user_email, place_uid=place_uid
    )

    # POST PLACES
    response = await api_client.post(
        UserVisitedPlaces.URL_PATH, json=place,
        headers={"token": TOKEN}
    )
    assert response.status == http.HTTPStatus.CREATED

    # GET PLACES
    response = await api_client.get(
        UserVisitedPlaces.URL_PATH,
        headers={"token": TOKEN}
    )
    assert response.status == http.HTTPStatus.OK

    # POST FEEDBACKS
    response = await api_client.post(
        UserFeedbacks.URL_PATH, json=feedback,
        headers={"token": TOKEN}
    )
    assert response.status == http.HTTPStatus.CREATED

    # GET FEEDBACKS
    response = await api_client.get(
        UserFeedbacks.URL_PATH,
        headers={"token": TOKEN}
    )
    assert response.status == http.HTTPStatus.OK

    # DELETE FEEDBACKS
    response = await api_client.get(
        url_for(UserFeedbacks.URL_PATH, place_uid=place_uid),
        headers={"token": TOKEN}
    )
    assert response.status == http.HTTPStatus.OK


async def test_invalid_token(api_client):
    place = generate_visited_place()

    user_email = place['user_email']
    place_uid = place['place_uid']

    feedback = generate_user_feedback(
        user_email=user_email, place_uid=place_uid
    )

    # POST PLACES
    # response = await api_client.post(
    #     UserVisitedPlaces.URL_PATH, json=place,
    #     headers={"token": 'somestring'}
    # )
    # assert response.status == http.HTTPStatus.UNAUTHORIZED

    # GET PLACES
    response = await api_client.get(
        url_for(UserVisitedPlaces.URL_PATH, user_email=''),
        headers={"token": 'somestring'}
    )
    assert response.status == http.HTTPStatus.UNAUTHORIZED

    # POST FEEDBACKS
    # response = await api_client.post(
    #     UserFeedbacks.URL_PATH, json=feedback,
    #     headers={"token": 'somestring'}
    # )
    # assert response.status == http.HTTPStatus.UNAUTHORIZED

    # GET FEEDBACKS
    response = await api_client.get(
        url_for(UserFeedbacks.URL_PATH, user_email=''),
        headers={"token": 'somestring'}
    )
    assert response.status == http.HTTPStatus.UNAUTHORIZED

    # DELETE FEEDBACKS
    response = await api_client.get(
        url_for(UserFeedbacks.URL_PATH, user_email='', place_uid=place_uid),
        headers={"token": 'somestring'}
    )
    assert response.status == http.HTTPStatus.UNAUTHORIZED


async def test_empty_token(api_client):
    place = generate_visited_place()

    user_email = place['user_email']
    place_uid = place['place_uid']

    feedback = generate_user_feedback(
        user_email=user_email, place_uid=place_uid
    )

    # POST PLACES
    # response = await api_client.post(
    #     UserVisitedPlaces.URL_PATH, json=place,
    # )
    # assert response.status == http.HTTPStatus.BAD_REQUEST

    # GET PLACES
    response = await api_client.get(
        url_for(UserVisitedPlaces.URL_PATH, user_email=''),
    )
    assert response.status == http.HTTPStatus.BAD_REQUEST

    # POST FEEDBACKS
    # response = await api_client.post(
    #     UserFeedbacks.URL_PATH, json=feedback,
    # )
    # assert response.status == http.HTTPStatus.BAD_REQUEST

    # GET FEEDBACKS
    response = await api_client.get(
        url_for(UserFeedbacks.URL_PATH, user_email=''),
    )
    assert response.status == http.HTTPStatus.BAD_REQUEST

    # DELETE FEEDBACKS
    response = await api_client.get(
        url_for(UserFeedbacks.URL_PATH, place_uid=place_uid),
    )
    assert response.status == http.HTTPStatus.BAD_REQUEST
