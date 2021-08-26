from http import HTTPStatus
from typing import Optional, Union

from aiohttp_pydantic import PydanticView
from aiohttp_pydantic.oas.typing import r200, r400, r201
from aiohttp.web_response import json_response
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from maps.api.handlers.base import BaseView
from maps.api.schema import (
    ErrorResponseSchema,
    GetUserFeedbacksResponse,
    PostUserFeedbacksRequest, PostUserFeedbacksResponse,
)
from maps.db.schema import (
    user_feedbacks_table as user_feedbacks_t
)


class UserFeedbacks(PydanticView, BaseView):
    URL_PATH = '/user_feedbacks'

    async def get(
        self, user_email: Optional[str] = 'maps@.y.r',
        *, token: Optional[str] = '',
    ) -> Union[r200[GetUserFeedbacksResponse], r400[ErrorResponseSchema]]:
        await self.check_email(user_email)

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
    ) -> Union[r201[PostUserFeedbacksResponse], r400[ErrorResponseSchema]]:
        user_email = feedback.user_email
        place_uid = feedback.place_uid
        feedback_rate = feedback.feedback_rate
        feedback_text = feedback.feedback_text

        await self.check_user_was_here(user_email, place_uid)

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
