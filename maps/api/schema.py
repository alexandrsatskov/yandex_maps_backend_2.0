"""
Модуль содержит схемы для валидации
данных в запросах и ответах.

Схемы валидации запросов *RequestSchema
используются в бою для валидации данных
отправленных клиентами.

Схемы валидации ответов *ResponseSchema
используются только при тестировании,
чтобы убедиться что обработчики возвращают
данные в корректном формате.
"""
from dataclasses import dataclass
from enum import Enum, unique
from typing import Union, List, Dict, Optional, Any

from pydantic import (
    BaseModel, EmailStr,
    conint, confloat, PositiveInt
)


@dataclass
class ScreenResolution:
    width: Union[int, float]
    height: Union[int, float]


class UserContext(str, Enum):
    default = 'DEFAULT'
    ugc = 'UGC'


@unique
class PlaceState(int, Enum):
    card = 1
    ico_btfl = 2
    ico_w_txt = 3
    ico_wo_txt = 4
    plain_point = 5


class ErrorSchema(BaseModel):
    code: str
    message: str
    fields: Optional[List[Dict[str, Any]]]


class ErrorResponseSchema(BaseModel):
    error: ErrorSchema


# TODO: try to create ORM pydantic schemas
# <------------- Places ------------->
class PlaceSchema(BaseModel):
    place_uid: str
    place_id: int
    latitude: confloat(ge=-90, le=90)
    longitude: confloat(ge=-180, le=180)


class GetVisitedPlaceResponse(PlaceSchema):
    state: PlaceState


class GetVisitedPlacesResponse(BaseModel):
    places: List[GetVisitedPlaceResponse]


class PostVisitedPlacesRequest(PlaceSchema):
    # TODO: change str -> EmailStr
    # TODO: remove it, add token header
    user_email: str


class PostVisitedPlacesResponse(BaseModel):
    place_uid: str


# <------------- UserFeedbacks ------------->
class UserFeedbackSchema(BaseModel):
    user_email: str
    place_uid: str
    feedback_rate: conint(ge=0, le=5)
    feedback_text: str


class GetUserFeedbacksResponse(BaseModel):
    feedbacks: List[UserFeedbackSchema]


class PostUserFeedbacksRequest(UserFeedbackSchema):
    pass


class PostUserFeedbacksResponse(BaseModel):
    id: PositiveInt
