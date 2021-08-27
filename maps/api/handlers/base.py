from http import HTTPStatus

from aiohttp import ClientSession
from aiohttp.web import View
from aiohttp.web_exceptions import HTTPBadRequest, HTTPUnauthorized
from sqlalchemy import exists, select, and_
from sqlalchemy.engine import Engine

from maps.db.schema import (
    users_table as users_t,
    places_table as places_t,
    user_places_table as user_places_t,
    user_feedbacks_table as user_feedbacks_t,
)


class BaseView(View):
    URL_PATH: str

    @property
    def pg(self) -> Engine:
        return self.request.app['pg']

    async def is_record_exists(self, stmt) -> bool:
        async with self.pg.connect() as conn:
            is_exists = await conn.execute(stmt)
        return is_exists.scalar()

    async def is_email_exists(self, user_email):
        stmt = select([
            exists().where(users_t.c.user_email == user_email)
        ])
        return await self.is_record_exists(stmt)

    async def check_email(self, user_email):
        stmt = select([
            exists().where(users_t.c.user_email == user_email)
        ])
        if not await self.is_record_exists(stmt):
            raise HTTPBadRequest(text=f"{user_email=} doesn't exist in database!")

    async def check_uid(self, place_uid):
        stmt = select([
            exists().where(places_t.c.place_uid == place_uid)
        ])
        if not await self.is_record_exists(stmt):
            raise HTTPBadRequest(text=f"{place_uid=} doesn't exist in database!")

    async def check_user_was_here(self, user_email, place_uid):
        stmt = select([
            exists().where(
                and_(
                    user_places_t.c.user_email == user_email,
                    user_places_t.c.place_uid == place_uid
                )
            )
        ])
        if not await self.is_record_exists(stmt):
            raise HTTPBadRequest(text=f"{user_email=} wasn't be in {place_uid=}!")

    async def check_user_left_feedback(self, user_email, place_uid):
        stmt = select([
            exists().where(
                and_(
                    user_feedbacks_t.c.user_email == user_email,
                    user_feedbacks_t.c.place_uid == place_uid
                )
            )
        ])
        if not await self.is_record_exists(stmt):
            raise HTTPBadRequest(text=f"The {user_email=} has no feedback for this {place_uid=}!")

    @staticmethod
    async def get_email_from_token(token: str) -> str:
        async with ClientSession() as session:
            url = 'https://login.yandex.ru/info'
            query_params = {'format': 'json'}
            headers = {'Authorization': f'OAuth {token}'}

            async with session.get(url, params=query_params, headers=headers) as resp:
                if resp.status == HTTPStatus.UNAUTHORIZED:
                    raise HTTPUnauthorized(text=f'Invalid token: {token=}')

                res = await resp.json()
                if not (user_email := res.get('default_email', None)):
                    raise HTTPBadRequest(text=f'Token with low permission scope: {token=}')

                return user_email

    async def get_email(self, user_email, token):
        if not user_email and not token:
            raise HTTPBadRequest(text='user_email or token not provided!')

        user_email = user_email or await self.get_email_from_token(token)
        return user_email
