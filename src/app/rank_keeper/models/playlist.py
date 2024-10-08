from rank_keeper.db import DB
from rank_keeper.models import model


class CRUDBase:
    @staticmethod
    async def execute(query, *args, **kwargs):
        async with DB() as db:
            result = await db.execute(query, *args, **kwargs)
        return result


class rank(CRUDBase):
    def __init__(self, name: int):
        self.name = name

    async def get(self):
        q = model.rank.select().where(self.name == model.rank.c.name)
        result = await self.execute(q)
        return await result.fetchone()

    async def set(self, **kwargs):
        q = (
            model.rank.update(None)
            .where(self.name == model.rank.c.name)
            .values(**kwargs)
        )
        await self.execute(q)
        return self

    async def delete(self):
        q = model.rank.delete(None).where(self.name == model.rank.c.name)
        await self.execute(q)
        return self

    @classmethod
    async def create(cls, **kwargs):
        q = model.rank.insert(None).values(**kwargs)
        rank = cls(kwargs['name'])
        await cls.execute(q)
        return rank

    @staticmethod
    async def get_all(cls):
        q = model.rank.select()
        results = await cls.execute(q)
        return await results.fetchall()