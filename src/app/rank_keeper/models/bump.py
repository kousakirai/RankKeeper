from rank_keeper.db import DB
from rank_keeper.models import model


class CRUDBase:
    @staticmethod
    async def execute(query, *args, **kwargs):
        async with DB() as db:
            result = await db.execute(query, *args, **kwargs)
        return result


class Bump(CRUDBase):
    def __init__(self, channel_id):
        self.channel_id = channel_id

    async def get(self):
        q = model.bump.select().where(self.channel_id == model.bump.c.id)
        result = await self.execute(q)
        return await result.fetchone()

    async def set(self, **kwargs):
        q = (
            model.bump.update(None)
            .where(self.channel_id == model.bump.c.id)
            .values(**kwargs)
        )
        await self.execute(q)
        return self

    async def delete(self):
        q = model.bump.delete(None).where(self.channel_id == model.bump.c.id)
        await self.execute(q)
        return self

    @classmethod
    async def create(cls, channel_id):
        q = model.bump.insert(None).values(id=channel_id)
        bump = cls(channel_id)
        await cls.execute(q)
        return bump

    @staticmethod
    async def get_all(cls):
        q = model.bump.select()
        results = await cls.execute(q)
        return await results.fetchall()
