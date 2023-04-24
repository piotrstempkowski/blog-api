FROM python:3.11

WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY pyproject.toml poetry.lock /code/
RUN pip install poetry && poetry config virtualenvs.create false && poetry install --without dev

COPY backend /code
