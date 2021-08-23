import random
from enum import EnumMeta
from http import HTTPStatus
from typing import Any, Dict, Iterable, List, Mapping, Optional, Union, Type

import faker
from aiohttp.test_utils import TestClient
from aiohttp.typedefs import StrOrURL
from aiohttp.web_urldispatcher import DynamicResource
from pydantic import validate_model, BaseModel

from analyzer.api.handlers.base import (
    BaseView
)
from analyzer.api.handlers import (
    UserVisitedPlaces, UserFeedbacks
)
from analyzer.api.schema import (
    GetVisitedPlacesResponse, GetVisitedPlaceResponse,
    PostVisitedPlacesResponse, PostUserFeedbacksResponse,
    GetUserFeedbacksResponse, UserContext
)
from analyzer.utils.pg import MAX_INTEGER

fake = faker.Faker('ru_RU')


def url_for(path: str, **kwargs) -> str:
    """
    Генерирует URL для динамического aiohttp маршрута с параметрами
    """
    kwargs = {
        key: str(value)  # Все значения должны быть str (для DynamicResource)
        for key, value in kwargs.items()
    }
    return str(DynamicResource(path).url_for(**kwargs))


def generate_visited_place(
    user_email: Optional[str] = None,
    place_uid: Optional[str] = None,
    place_id: Optional[int] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Создает и возвращает пользовательское
    посещенное место, автоматически генерируя
    данные для не указанных полей.
    """
    if user_email is None:
        user_email = fake.email()

    if place_uid is None:
        place_uid = f'ymapsbm1://org?oid={random.randint(0, (10 ** 11) - 1)}'

    if place_id is None:
        place_id = random.randint(0, (10 ** 10) - 1)

    if latitude is None:
        latitude = float(fake.latitude())

    if longitude is None:
        longitude = float(fake.longitude())

    return locals()


def generate_user_feedback(
    user_email: Optional[str] = None,
    place_uid: Optional[str] = None,
    feedback_rate: Optional[int] = None,
    feedback_text: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Создает и возвращает пользовательский
    отзыв, автоматически генерируя данные
    для не указанных полей.
    """
    if user_email is None:
        user_email = fake.email()

    if place_uid is None:
        place_uid = f'ymapsbm1://org?oid={random.randint(0, (10 ** 11) - 1)}'

    if feedback_rate is None:
        feedback_rate = random.randint(0, 5)

    if feedback_text is None:
        feedback_text = fake.file_name()

    return locals()


async def post_record(
    client: TestClient,
    record: Dict[str, Any],
    pydantic_view: Type[BaseView],
    pydantic_schema: Type[BaseModel],
    expected_status: Union[int, EnumMeta] = HTTPStatus.CREATED,
    **request_kwargs
) -> Dict[str, str]:
    response = await client.post(
        pydantic_view.URL_PATH, json=record, **request_kwargs
    )
    assert response.status == expected_status

    if response.status == HTTPStatus.CREATED:
        data: dict = await response.json()
        # validate_model returns None, if no errors
        *_, errors = validate_model(pydantic_schema, data)
        assert errors is None, errors
        return data


async def get_visited_places(
    client: TestClient,
    user_email: str,
    user_context: UserContext,
    latitude: Optional[float] = 1,
    longitude: Optional[float] = 1,
    expected_status: Union[int, EnumMeta] = HTTPStatus.OK,
    **request_kwargs
) -> dict:
    url = f'/visited_places?user_email={user_email}&user_context={user_context}&latitude={latitude}&longitude={longitude}'
    response = await client.get(
            url,
        # url_for(UserVisitedPlaces.URL_PATH,
        #         user_email=user_email,
        #         user_context=user_context,
        #         latitude=latitude,
        #         longitude=longitude),
        **request_kwargs
    )
    assert response.status == expected_status, url

    if response.status == HTTPStatus.OK:
        data = await response.json()
        *_, errors = validate_model(GetVisitedPlacesResponse, data)
        assert errors is None, errors
        # hack
        if data['places']:
            return data['places'][0]
        return data['places']


async def get_user_feedbacks(
    client: TestClient,
    user_email: str,
    expected_status: Union[int, EnumMeta] = HTTPStatus.OK,
    **request_kwargs
) -> List[dict]:
    url = f'/user_feedbacks?user_email={user_email}'
    response = await client.get(url, **request_kwargs)

    assert response.status == expected_status, url

    if response.status == HTTPStatus.OK:
        data = await response.json()
        *_, errors = validate_model(GetUserFeedbacksResponse, data)
        assert errors is None, errors
        return data['feedbacks']
#
#
# async def patch_citizen(
#         client: TestClient,
#         import_id: int,
#         citizen_id: int,
#         data: Mapping[str, Any],
#         expected_status: Union[int, EnumMeta] = HTTPStatus.OK,
#         str_or_url: StrOrURL = CitizenView.URL_PATH,
#         **request_kwargs
# ):
#     response = await client.patch(
#         url_for(str_or_url, import_id=import_id,
#                 citizen_id=citizen_id),
#         json=data,
#         **request_kwargs
#     )
#     assert response.status == expected_status
#     if response.status == HTTPStatus.OK:
#         data = await response.json()
#         errors = PatchCitizenResponseSchema().validate(data)
#         assert errors == {}
#         return data['data']
