from aiohttp.web_exceptions import HTTPBadRequest
from sqlalchemy import exists, select
from aiohttp_pydantic import PydanticView
from sqlalchemy.engine import Engine

from analyzer.db.schema import (
    users_table as users_t,
    places_table as places_t
)


class BaseView(PydanticView):
    URL_PATH: str

    @property
    def pg(self) -> Engine:
        return self.request.app['pg']

    async def check_email_exists(self, user_email):
        stmt = select([
            exists().where(users_t.c.user_email == user_email)
        ])
        async with self.pg.connect() as conn:
            is_exists = await conn.execute(stmt)

        if not is_exists.scalar():
            raise HTTPBadRequest(text=f"{user_email=} doesn't exist in database!")

    async def check_uid_exists(self, place_uid):
        stmt = select([
            exists().where(places_t.c.place_uid == place_uid)
        ])
        async with self.pg.connect() as conn:
            is_exists = await conn.execute(stmt)

        if not is_exists.scalar():
            raise HTTPBadRequest(text=f"{place_uid=} doesn't exist in database!")
