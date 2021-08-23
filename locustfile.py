import logging
import random
from http import HTTPStatus

from faker import Faker
from locust import HttpUser, constant, task

from analyzer.api.schema import (
    UserContext
)
from analyzer.api.handlers import (
    UserVisitedPlaces, UserFeedbacks
)
from analyzer.utils.testing import (
    generate_user_feedback,
    generate_visited_place
)

fake = Faker('ru_RU')


class AnalyzerTaskSet(HttpUser):
    wait_time = constant(1)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.round = 0

    def request(self, method, path, expected_status, **kwargs):
        with self.client.request(
                method, path, catch_response=True, **kwargs
        ) as resp:
            if resp.status_code != expected_status:
                resp.failure(f'expected status {expected_status}, '
                             f'got {resp.status_code}')
            print(kwargs, resp.text)
            logging.info(
                'round %r: %s %s, http status %d (expected %d), took %rs',
                self.round, method, path, resp.status_code, expected_status,
                resp.elapsed.total_seconds()
            )
            return resp

    def post_user_feedbacks(self, data):
        route = UserFeedbacks.URL_PATH
        self.request('POST', route, HTTPStatus.CREATED,
                     name=route, json=data)

    def post_visited_places(self, data):
        route = UserVisitedPlaces.URL_PATH
        self.request('POST', route, HTTPStatus.CREATED,
                     name=route, json=data)

    def get_visited_places(self, user_email):
        state = UserContext.ugc.value
        latitude = float(fake.latitude())
        longitude = float(fake.longitude())
        zoom = random.uniform(2, 21)
        device_width = 1440
        device_height = 2392

        route = UserVisitedPlaces.URL_PATH
        url = f'{route}?latitude={latitude}&longitude={longitude}&zoom={zoom}&device_width={device_width}&device_height={device_height}&state={state}&user_email={user_email}'
        self.request('GET', url, HTTPStatus.OK, name=route)

    def get_user_feedbacks(self, user_email):
        route = UserFeedbacks.URL_PATH
        url = f'{route}?user_email={user_email}'
        self.request('GET', url, HTTPStatus.OK, name=route)

    @task
    def workflow(self):
        self.round += 1

        # Так как отзыв не может оставлять пользователь
        # чьего email'a и place_uid'a нет в базе, то нужно
        # вначале заносить эти данные в базу с помощью ручки
        # /visited_places [POST].
        # Соответственно данные user_email, place_uid должны быть
        # одинаковы для всех тестируемых ручек
        user_email = fake.email()
        place_uid = f'ymapsbm1://org?oid={random.randint(0, (10 ** 11) - 1)}'

        data = generate_visited_place(user_email, place_uid)
        self.post_visited_places(data=data)

        data = generate_user_feedback(user_email, place_uid)
        self.post_user_feedbacks(data=data)

        self.get_visited_places(user_email)
        self.get_user_feedbacks(user_email)
