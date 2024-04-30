set -eu
cd alembic
python3 -m alembic upgrade head
python3 -m alembic revision --autogenerate
python3 -m alembic upgrade head
cd ..
python -m rank_keeper