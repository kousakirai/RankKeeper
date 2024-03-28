from rank_keeper.models import model
from rank_keeper.db import DB


class CRUDBase:
    @staticmethod
    async def execute(query, *args, **kwargs):
        async with DB() as db:
            result = await db.execute(query, *args, **kwargs)
        return result


class Panel(CRUDBase):
    def __init__(self, message_id):
        self.message_id = message_id

    async def get(self):
        q = model.panel.select().where(self.message_id == model.panel.c.id)
        result = await self.execute(q)
        return await result.fetchone()

    async def set(self, **kwargs):
        q = model.panel.update(None).where(
            self.message_id == model.panel.c.id
        ).values(**kwargs)
        await self.execute(q)
        return self

    async def delete(self):
        q = model.panel.delete(None).where(self.message_id == model.panel.c.id)
        await self.execute(q)
        return self

    @classmethod
    async def create(cls, message_id):
        q = model.panel.insert(None).values(id=message_id)
        panel = cls(message_id)
        await cls.execute(q)
        return panel

    @staticmethod
    async def get_all(cls):
        q = model.panel.select()
        results = await cls.execute(q)
        return await results.fetchall()