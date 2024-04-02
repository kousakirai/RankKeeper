import os
import asyncio
from aiomysql.sa import create_engine
from logging import getLogger


LOG = getLogger(__name__)


class DB:
    async def __aenter__(self, loop=None):
        if loop is None:
            loop = asyncio.get_event_loop()
        LOG.info('Connecting to MySQL...')
        engine = await create_engine(
            user=os.environ["MYSQL_USER"],
            db=os.environ["MYSQL_DATABASE"],
            host="mysql",
            password=os.environ["MYSQL_PASSWORD"],
            charset="utf8",
            port=3306,
            autocommit=True,
            loop=loop
        )
        self._connection = await engine.acquire()
        LOG.info('Connected to MySQL.')
        return self

    async def __aexit__(self, *args, **kwargs):
        await self._connection.close()

    async def execute(self, query, *args, **kwargs):
        return await self._connection.execute(query, *args, **kwargs)