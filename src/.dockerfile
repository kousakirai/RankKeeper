FROM python:3.9.19 as builder
WORKDIR /bot
RUN apt update -y && \
    apt upgrade -y
COPY ./app/pyproject.toml  /bot/
RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH /root/.local/bin:$PATH

RUN poetry config virtualenvs.create false && \
    poetry install
RUN pip install alembic
FROM python:3.9-slim
WORKDIR /bot

ENV PYTHONBUFFERED=1
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages

COPY . /bot