from http import HTTPStatus
from typing import Optional, Union

from aiohttp.web_exceptions import HTTPBadRequest
from aiohttp_pydantic.oas.typing import r200, r400, r201

from aiohttp.web_response import json_response
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from analyzer.api.schema import (
    GetUserFeedbacksResponse,
    PostUserFeedbacksRequest, PostUserFeedbacksResponse,
)
from analyzer.db.schema import (
    user_feedbacks_table as user_feedbacks_t
)
# from http import HTTPStatus
#
# from aiohttp.web_exceptions import HTTPNotFound
# from aiohttp.web_response import json_response
# from aiohttp_apispec import docs, request_schema, response_schema
# from asyncpg import ForeignKeyViolationError
# from marshmallow import ValidationError
# from sqlalchemy import and_, or_
#
# from analyzer.api.schema import PatchCitizenResponseSchema, PatchCitizenSchema
# from analyzer.db.schema import citizens_table, relations_table
#
from analyzer.api.handlers.base import BaseView


# from .query import CITIZENS_QUERY
#
#
# class UserFeedbacks(BaseImportView):
#     URL_PATH = r'/user_feedbacks'
#
#     @docs(summary='Отобразить жителей для указанной выгрузки')
#     @response_schema(CitizensResponseSchema(), code=HTTPStatus.OK.value)
#     # await self.check_import_exists()
#     #
#     # query = CITIZENS_QUERY.where(
#     #     citizens_t.c.import_id == self.import_id
#     # )
#     # body = SelectQuery(query, self.pg.transaction())
#     # return json_response(body)
#
#     # @staticmethod
#     # async def acquire_lock(conn, import_id):
#     #     await conn.execute('SELECT pg_advisory_xact_lock($1)', import_id)
#
#     # @docs(summary='Получить отзывы пользователя')
#     # @request_schema(PatchCitizenSchema())
#     # @response_schema(PatchCitizenResponseSchema(), code=HTTPStatus.OK.value)
#     # async def patch(self):
#         # Транзакция требуется чтобы в случае ошибки (или отключения клиента,
#         # не дождавшегося ответа) откатить частично добавленные изменения, а
#         # также для получения транзакционной advisory-блокировки.
#         # async with self.pg.transaction() as conn:
#
#             # Блокировка позволит избежать состояние гонки между конкурентными
#             # запросами на изменение родственников.
#             # await self.acquire_lock(conn, self.import_id)
#
#             # Получаем информацию о жителе
#             # citizen = await self.get_citizen(conn, self.import_id,
#             #                                  self.citizen_id)
#             # if not citizen:
#             #     raise HTTPNotFound()
#
#             # Обновляем таблицу citizens
#             # await self.update_citizen(conn, self.import_id, self.citizen_id,
#             #                           self.request['data'])
#
#         # return json_response({'data': citizen})
#


class UserFeedbacks(BaseView):
    URL_PATH = '/user_feedbacks'

    async def get(
        self, user_email: Optional[str] = 'string',
        *, token: Optional[str] = '',
    ) -> Union[r200[GetUserFeedbacksResponse], r400[HTTPBadRequest]]:
        await self.check_email_exists(user_email)

        stmt = (
            select([
                user_feedbacks_t.c.user_email,
                user_feedbacks_t.c.place_uid,
                user_feedbacks_t.c.feedback_rate,
                user_feedbacks_t.c.feedback_text,
            ])
            .where(user_feedbacks_t.c.user_email == user_email)
        )
        async with self.pg.connect() as conn:
            res = await conn.execute(stmt)

        return json_response(
            {"feedbacks": [
                {**feedback}
                for feedback in res.mappings().all()
            ]},
            status=HTTPStatus.OK
        )

    async def post(
        self, feedback: PostUserFeedbacksRequest,
        *, token: Optional[str] = '',
    ) -> Union[r201[PostUserFeedbacksResponse], r400[HTTPBadRequest]]:
        user_email = feedback.user_email
        place_uid = feedback.place_uid
        feedback_rate = feedback.feedback_rate
        feedback_text = feedback.feedback_text

        await self.check_email_exists(user_email)
        await self.check_uid_exists(place_uid)

        async with self.pg.begin() as conn:
            stmt = (
                insert(user_feedbacks_t)
                    .values(
                    user_email=user_email,
                    place_uid=place_uid,
                    feedback_rate=feedback_rate,
                    feedback_text=feedback_text
                )
                    .returning(user_feedbacks_t.c.id)
                    .on_conflict_do_update(
                    index_elements=[user_feedbacks_t.c.user_email, user_feedbacks_t.c.place_uid],
                    set_=dict(feedback_rate=feedback_rate, feedback_text=feedback_text),
                )
            )
            res = await conn.execute(stmt)

        return json_response(
            {"id": res.scalar()},
            status=HTTPStatus.CREATED
        )
