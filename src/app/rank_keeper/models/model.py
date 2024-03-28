from sqlalchemy import MetaData, Table, Column, BigInteger, String, Integer, PickleType

meta = MetaData()

"""
1=PC(origin, steam)
2=PS4
3=Switch
"""

user = Table(
    "user",
    meta,
    Column("id", BigInteger(), nullable=False, primary_key=True),
    Column("speaker", Integer, server_default='2', nullable=False),
    Column("platform", Integer, nullable=True),
    Column("name", String(100), nullable=True),
)

guild = Table(
    "guild",
    meta,
    Column("id", BigInteger(), nullable=False, primary_key=True),
    Column("volume", Integer, server_default='100', nullable=False)
)

panel = Table(
    'panel',
    meta,
    Column('message_id', BigInteger(), nullable=False, primary_key=True),
    Column('description', String(200), nullable=False),
    Column('role_list', PickleType, nullable=False),
)