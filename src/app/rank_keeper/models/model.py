from sqlalchemy import MetaData, Table, Column, BigInteger, String, PickleType


meta = MetaData()


bump = Table(
    'bump',
    meta,
    Column('id', BigInteger(), nullable=False, primary_key=True),
    Column('role_id', BigInteger(), nullable=False),
    Column('bump_time', BigInteger(), nullable=True)
)

rank = Table(
    "rank",
    meta,
    Column("name", String(255), nullable=False, primary_key=True),
    Column("role_id", BigInteger(), nullable=False),
)
