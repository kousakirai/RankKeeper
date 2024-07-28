from rank_keeper.db import DB
from rank_keeper.models import model


class CRUDBase:
    @staticmethod
    async def execute(query, *args, **kwargs):
        async with DB() as db:
            result = await db.execute(query, *args, **kwargs)
        return result


class Bump(CRUDBase):
    def __init__(self, title: str):
        self.title = title

    async def get(self):
        q = model.bump.select().where(self.title == model.playlist.c.title)
        result = await self.execute(q)
        return await result.fetchone()

    async def set(self, **kwargs):
        q = (
            model.bump.update(None)
            .where(self.title == model.playlist.c.title)
            .values(**kwargs)
        )
        await self.execute(q)
        return self

    async def delete(self):
        q = model.bump.delete(None).where(self.title == model.playlist.c.title)
        await self.execute(q)
        return self

    @classmethod
    async def create(cls, **kwargs):
        q = model.bump.insert(None).values(**kwargs)
        bump = cls(kwargs['title'])
        await cls.execute(q)
        return bump

    @staticmethod
    async def get_all(cls):
        q = model.bump.select()
        results = await cls.execute(q)
        return await results.fetchall()