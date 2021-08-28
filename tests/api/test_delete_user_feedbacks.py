import pytest

from maps.utils.testing import (
    get_user_feedbacks, post_user_feedbacks,
    get_visited_places, post_visited_places,
    delete_user_feedbacks,
)
from maps.utils.generating_test_data import (
    generate_visited_place, generate_user_feedback,
)

USER_EMAIL = 'maps@.y.r'
PLACE_UID = 'myawesomeplace'


@pytest.mark.parametrize('user_email,places', (
    # Обработчик должен корректно удалять отзыв
    (
        USER_EMAIL,
        [generate_visited_place(user_email=USER_EMAIL)],
    ),
    # Обработчик должен корректно удалять все отзывы
    (
        USER_EMAIL,
        [generate_visited_place(user_email=USER_EMAIL) for _ in range(3)]
    ),
))
async def test_delete_sole_feedback_wo_other_users(api_client, user_email, places):
    feedback_ids = []

    for place in places:
        await post_visited_places(api_client, place)

        # Генерируем фидбек на основе вставленных данные
        feedback = generate_user_feedback(
            user_email=user_email,
            place_uid=place['place_uid']
        )
        id_ = await post_user_feedbacks(api_client, feedback)
        feedback_ids.append(id_)

    # Удаляем отзыв
    deleted = await delete_user_feedbacks(api_client, user_email=user_email)
    assert sorted(deleted['feedbacks'], key=lambda k: k['id']) == feedback_ids

    # Проверяем что отзывы действительно удалены
    feedbacks = await get_user_feedbacks(
        api_client, user_email=user_email
    )
    assert feedbacks == {'feedbacks': []}


@pytest.mark.parametrize('user_places,places,condition', (
    # Обработчик должен корректно удалять конкретный отзыв
    (
        [generate_visited_place(user_email=USER_EMAIL, place_uid=PLACE_UID)],
        [],
        'ONE',
    ),
    # Обработчик должен корректно удалять отзыв
    # конкретного пользователя не затрагивая отзывы
    # других пользователей
    (
        [generate_visited_place(user_email=USER_EMAIL, place_uid=PLACE_UID)],
        [generate_visited_place() for _ in range(5)],
        'ONE',
    ),
    # Обработчик должен корректно удалять все отзывы
    # конкретного пользователя не затрагивая отзывы
    # других пользователей
    (
        [generate_visited_place(user_email=USER_EMAIL) for _ in range(3)],
        [generate_visited_place() for _ in range(5)],
        'ALL'
    ),
))
async def test_delete_sole_feedback(api_client, user_places, places, condition):
    feedback_ids = []

    for place in user_places:
        await post_visited_places(api_client, place)

        feedback = generate_user_feedback(
            user_email=place['user_email'],
            place_uid=place['place_uid']
        )
        id_ = await post_user_feedbacks(api_client, feedback)
        feedback_ids.append(id_)

    for place in places:
        await post_visited_places(api_client, place)

        feedback = generate_user_feedback(
            user_email=place['user_email'],
            place_uid=place['place_uid']
        )
        await post_user_feedbacks(api_client, feedback)

    if condition == 'ONE':
        # Удаляем отзыв
        deleted = await delete_user_feedbacks(api_client, user_email=USER_EMAIL, place_uid=PLACE_UID)
        assert sorted(deleted['feedbacks'], key=lambda k: k['id']) == feedback_ids

    elif condition == 'ALL':
        deleted = await delete_user_feedbacks(api_client, user_email=USER_EMAIL)
        assert sorted(deleted['feedbacks'], key=lambda k: k['id']) == feedback_ids

    # Проверяем что отзывы действительно удалены
    feedbacks = await get_user_feedbacks(
        api_client, user_email=USER_EMAIL
    )
    assert feedbacks == {'feedbacks': []}


@pytest.mark.parametrize('user_places,places', (
    # Обработчик должен корректно удалять отзыв
    # конкретного пользователя
    # не затрагивая другие его отзывы и отзывы других пользователей
    (
        [generate_visited_place(user_email=USER_EMAIL)
         for _ in range(2)],
        [generate_visited_place() for _ in range(1)],
    ),
))
async def test_delete_sole_in_others_feedback(api_client, user_places, places):
    user_places[0]['place_uid'] = PLACE_UID
    feedback_ids = [{"id": 1}]
    user_feedbacks = []

    for place in user_places:
        await post_visited_places(api_client, place)

        feedback = generate_user_feedback(
            user_email=place['user_email'],
            place_uid=place['place_uid']
        )
        user_feedbacks.append(feedback)
        await post_user_feedbacks(api_client, feedback)

    for place in places:
        await post_visited_places(api_client, place)

        feedback = generate_user_feedback(
            user_email=place['user_email'],
            place_uid=place['place_uid']
        )
        await post_user_feedbacks(api_client, feedback)

    deleted = await delete_user_feedbacks(api_client, user_email=USER_EMAIL, place_uid=PLACE_UID)
    assert sorted(deleted['feedbacks'], key=lambda k: k['id']) == feedback_ids

    # Проверяем что отзывы остались, кроме удаленного
    feedbacks = await get_user_feedbacks(
        api_client, user_email=USER_EMAIL
    )
    assert feedbacks == {'feedbacks': [feedback for feedback in user_feedbacks[1:]]}
