FROM python:3.10.14 as builder
WORKDIR /bot

RUN apt update -y && \
    apt upgrade -y

COPY ./app/poetry.lock  /bot/
COPY ./app/pyproject.toml /bot/
RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH /root/.local/bin:$PATH

RUN poetry config virtualenvs.create false && \
    poetry install
RUN pip install alembic
FROM python:3.10.14-slim
WORKDIR /bot
RUN apt update && apt install sudo
RUN sudo apt install -y ffmpeg

ENV PYTHONBUFFERED=1
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages

COPY . /bot