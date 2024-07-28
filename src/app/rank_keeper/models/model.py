from sqlalchemy import MetaData, Table, Column, BigInteger, String, PickleType


meta = MetaData()


bump = Table(
    'bump',
    meta,
    Column('id', BigInteger(), nullable=False, primary_key=True),
    Column('role_id', BigInteger(), nullable=False),
    Column('bump_time', BigInteger(), nullable=True)
)

playlist = Table(
    'playlist',
    meta,
    Column('title', String(50), nullable=False, primary_key=True),
    Column('author', String(50), nullable=False),
    Column('list', PickleType(), nullable=False)
)