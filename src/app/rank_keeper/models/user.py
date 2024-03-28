from rank_keeper.models import model
from rank_keeper.db import DB


class CRUDBase:
    @staticmethod
    async def execute(query, *args, **kwargs):
        async with DB() as db:
            result = await db.execute(query, *args, **kwargs)
        return result


class User(CRUDBase):
    def __init__(self, user_id):
        self.user_id = user_id

    async def get(self):
        q = model.user.select().where(self.user_id == model.user.c.id)
        result = await self.execute(q)
        return await result.fetchone()

    async def set(self, **kwargs):
        q = model.user.update(None).where(
            self.user_id == model.user.c.id
        ).values(**kwargs)
        await self.execute(q)
        return self

    async def delete(self):
        q = model.user.delete(None).where(self.user_id == model.user.c.id)
        await self.execute(q)
        return self

    @classmethod
    async def create(cls, **kwargs):
        q = model.user.insert(None).values(**kwargs)
        user = cls(**kwargs['id'])
        await cls.execute(q)
        return user

    @staticmethod
    async def get_all(cls):
        q = model.user.select()
        results = await cls.execute(q)
        return await results.fetchall()